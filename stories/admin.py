from django.contrib import admin
from .models import Story, StoryCollection

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'collection', 'genre', 'length', 'tone', 'is_public', 'is_favorite', 'rating', 'created_at']
    list_filter = ['genre', 'length', 'tone', 'is_public', 'is_favorite', 'rating', 'collection', 'created_at']
    search_fields = ['title', 'keywords', 'content', 'user__username', 'collection__name']
    readonly_fields = ['created_at', 'updated_at', 'generation_time', 'word_count']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'keywords', 'collection')
        }),
        ('Generation Parameters', {
            'fields': ('genre', 'length', 'tone')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Settings', {
            'fields': ('is_public', 'is_favorite', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'generation_time', 'ai_model_used', 'word_count'),
            'classes': ('collapse',)
        })
    )
    
    def word_count(self, obj):
        return obj.word_count
    word_count.short_description = 'Words'

@admin.register(StoryCollection)
class StoryCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'story_count', 'total_words', 'average_rating', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'story_count', 'total_words', 'average_rating']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'name', 'description')
        }),
        ('Appearance', {
            'fields': ('color', 'icon')
        }),
        ('Settings', {
            'fields': ('is_default',)
        }),
        ('Statistics', {
            'fields': ('story_count', 'total_words', 'average_rating', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def story_count(self, obj):
        return obj.story_count
    story_count.short_description = 'Stories'
    
    def total_words(self, obj):
        return f"{obj.total_words:,}"
    total_words.short_description = 'Total Words'
    
    def average_rating(self, obj):
        avg = obj.average_rating
        return f"{avg:.1f}★" if avg else "No ratings"
    average_rating.short_description = 'Avg Rating'
