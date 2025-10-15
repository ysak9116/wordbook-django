from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Folder, Term
from .forms import TermForm


def folder_list(request):
    folders = Folder.objects.annotate(term_count=Count("terms"))
    return render(request, "flashcards/folder_list.html", {"folders": folders})


def folder_create(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        if name:
            Folder.objects.get_or_create(name=name)
            messages.success(request, f"フォルダ「{name}」を作成しました。")
            return redirect("flashcards:folder_list")
        messages.error(request, "フォルダ名を入力してください。")
    return render(request, "flashcards/folder_create.html")


def folder_delete(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    if request.method == "POST":
        name = folder.name
        folder.delete()
        messages.warning(request, f"フォルダ「{name}」を削除しました。")
        return redirect("flashcards:folder_list")
    return render(request, "flashcards/folder_delete.html", {"folder": folder})


# --- ここより下：単語の本実装 ---


def term_list(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    status = request.GET.get("status")
    qs = folder.terms.all().order_by("term")
    valid = {s for s, _ in Term.Status.choices}
    if status in valid:
        qs = qs.filter(status=status)
    return render(
        request,
        "flashcards/term_list.html",
        {
            "folder": folder,
            "terms": qs,
            "status": status,
        },
    )


def term_create(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    if request.method == "POST":
        form = TermForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # 同一フォルダ・同一用語は上書き更新
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
    obj = get_object_or_404(Term, pk=pk)
    folder_id = obj.folder_id
    if request.method == "POST":
        name = obj.term
        obj.delete()
        messages.warning(request, f"「{name}」を削除しました。")
        return redirect("flashcards:term_list", folder_id=folder_id)
    return render(request, "flashcards/term_delete.html", {"obj": obj})


def term_toggle_status(request, pk, next_status):
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
