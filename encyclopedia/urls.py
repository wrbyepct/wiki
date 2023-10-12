from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry_title>", views.render_entry, name="entry"),
    path("results", views.render_results, name="results"),
    path("newpage", views.render_new_page, name="new_page" ),
    path("edit", views.render_edit, name="edit")
]
