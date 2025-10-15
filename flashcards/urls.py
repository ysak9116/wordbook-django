from django.urls import path
from . import views

app_name = "flashcards"

urlpatterns = [
    # フォルダ
    path("folders/", views.folder_list, name="folder_list"),
    path("folders/create/", views.folder_create, name="folder_create"),  # ←これが必須
    path("folders/<int:pk>/delete/", views.folder_delete, name="folder_delete"),
    # 単語（特定フォルダ）
    path("folders/<int:folder_id>/terms/", views.term_list, name="term_list"),
    path(
        "folders/<int:folder_id>/terms/create/", views.term_create, name="term_create"
    ),
    # 単語（編集・削除）
    path("terms/<int:pk>/edit/", views.term_edit, name="term_edit"),
    path("terms/<int:pk>/delete/", views.term_delete, name="term_delete"),
    # 状態切替
    path(
        "terms/<int:pk>/toggle/<str:next_status>/",
        views.term_toggle_status,
        name="term_toggle_status",
    ),
]
