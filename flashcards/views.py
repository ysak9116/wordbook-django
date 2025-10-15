from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Folder, Term
from .forms import TermForm


# =========================
# フォルダ
# =========================


def folder_list(request):
    """フォルダ一覧（用語数付き）"""
    folders = Folder.objects.annotate(term_count=Count("terms"))
    return render(request, "flashcards/folder_list.html", {"folders": folders})


def folder_create(request):
    """フォルダ作成"""
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        if name:
            Folder.objects.get_or_create(name=name)
            messages.success(request, f"フォルダ「{name}」を作成しました。")
            return redirect("flashcards:folder_list")
        messages.error(request, "フォルダ名を入力してください。")
    return render(request, "flashcards/folder_create.html")


@require_POST
def folder_delete(request, pk):
    """
    フォルダ削除（POST専用）
    - “フォルダ詳細（用語一覧）”ページの削除ボタンから直接POSTする想定
    """
    folder = get_object_or_404(Folder, pk=pk)

    # 必要なら所有者チェックや権限チェックをここで
    # if folder.owner_id != request.user.id:
    #     messages.error(request, "このフォルダを削除する権限がありません。")
    #     return redirect("flashcards:term_list", folder_id=folder.id)

    # 必要なら「空フォルダのみ削除可」にする
    # if folder.terms.exists():
    #     messages.error(request, "このフォルダには用語があるため削除できません。")
    #     return redirect("flashcards:term_list", folder_id=folder.id)

    name = folder.name
    folder.delete()  # Term の FK が CASCADE なら中身も一緒に削除
    messages.warning(request, f"フォルダ「{name}」を削除しました。")
    return redirect("flashcards:folder_list")


# =========================
# 用語（フォルダ詳細）
# =========================


def term_list(request, folder_id):
    """フォルダ内の用語一覧（状態でフィルタ可能）"""
    folder = get_object_or_404(Folder, pk=folder_id)
    status = request.GET.get("status")
    qs = folder.terms.all().order_by("term")
    valid = {s for s, _ in Term.Status.choices}
    if status in valid:
        qs = qs.filter(status=status)
    return render(
        request,
        "flashcards/term_list.html",
        {"folder": folder, "terms": qs, "status": status},
    )


def term_create(request, folder_id):
    """用語の新規作成（同一フォルダ・同一用語は上書き更新）"""
    folder = get_object_or_404(Folder, pk=folder_id)
    if request.method == "POST":
        form = TermForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            obj, created = Term.objects.get_or_create(
                folder=data["folder"],
                term=data["term"],
                defaults={
                    "reading": data.get("reading", ""),
                    "meaning": data.get("meaning", ""),
                    "status": data.get("status") or Term.Status.NEW,
                },
            )
            if not created:
                obj.reading = data.get("reading", obj.reading)
                obj.meaning = data.get("meaning", obj.meaning)
                obj.status = data.get("status") or obj.status
                obj.save()
                messages.info(request, f"「{obj.term}」を上書き更新しました。")
            else:
                messages.success(request, f"「{obj.term}」を追加しました。")
            return redirect("flashcards:term_list", folder_id=folder.id)
    else:
        form = TermForm(initial={"folder": folder, "status": Term.Status.NEW})
    return render(
        request,
        "flashcards/term_form.html",
        {"form": form, "folder": folder, "mode": "create"},
    )


def term_edit(request, pk):
    """用語の編集"""
    obj = get_object_or_404(Term, pk=pk)
    if request.method == "POST":
        form = TermForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"「{obj.term}」を更新しました。")
            return redirect("flashcards:term_list", folder_id=obj.folder_id)
    else:
        form = TermForm(instance=obj)
    return render(
        request,
        "flashcards/term_form.html",
        {"form": form, "folder": obj.folder, "mode": "edit"},
    )


def term_delete(request, pk):
    """用語の削除（確認→POST）"""
    obj = get_object_or_404(Term, pk=pk)
    folder_id = obj.folder_id
    if request.method == "POST":
        name = obj.term
        obj.delete()
        messages.warning(request, f"「{name}」を削除しました。")
        return redirect("flashcards:term_list", folder_id=folder_id)
    return render(request, "flashcards/term_delete.html", {"obj": obj})


def term_toggle_status(request, pk, next_status):
    """用語の状態トグル"""
    obj = get_object_or_404(Term, pk=pk)
    valid = {s for s, _ in Term.Status.choices}
    if next_status not in valid:
        messages.error(request, "不正な状態です。")
    else:
        obj.status = next_status
        obj.save(update_fields=["status"])
        messages.success(
            request, f"状態を「{obj.get_status_display()}」に変更しました。"
        )
    return redirect("flashcards:term_list", folder_id=obj.folder_id)
