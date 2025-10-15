from django.db import models
from django.utils import timezone


class Folder(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Term(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "未学習"
        LEARNING = "learning", "学習中"
        MASTERED = "mastered", "習得済み"

    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="terms")
    term = models.CharField(max_length=100)
    reading = models.CharField(max_length=100, blank=True)
    meaning = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["term"]
        constraints = [
            models.UniqueConstraint(
                fields=["folder", "term"], name="uniq_term_per_folder"
            )
        ]

    def __str__(self):
        return f"{self.term} ({self.folder})"
