from django.contrib import admin
from .models import Category, Skill, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # auto-fills slug as you type the name


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'price_type', 'created_at']
    list_filter = ['category', 'price_type', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'skill', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__username', 'skill__title', 'comment']
    readonly_fields = ['created_at']
