from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Text_to_speech


@admin.register(Text_to_speech)
class Text_to_speechAdmin(admin.ModelAdmin):
    list_display = (
        "get_voice",
        "text",
        "file_name",
        "created_at",
    )
    search_fields = ("text", "file_name")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("text", "file_name")}),
        ("Важные даты", {"fields": ("created_at",)}),
    )

    readonly_fields = ("created_at",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("file_name",) + self.readonly_fields
        return self.readonly_fields

    def get_voice(self, obj):
        audio_tag = f'''
            <audio style="border: 1px solid rgb(188, 255, 188); border-radius: 10px; width: 100px; max-width: 400px; margin: 20px 0;
                        display: flex; align-items: center; justify-content: space-between; background-color: #def8d4; padding: 10px; border-radius: 5px;" 
                src="{obj.path_file.url}" controls>
                <button style="background-color: #3498db; color: #fff; border: none; border-radius: 3px; cursor: pointer; padding: 5px 10px; margin: 0 5px; font-size: 14px; transition: background-color 0.3s ease;"
                        onmouseover="this.style.backgroundColor='#2980b9'" onmouseout="this.style.backgroundColor='#3498db'">
                    Play
                </button>
                <!-- Добавьте другие элементы управления аудиоплеером по вашему выбору -->
            </audio>
        '''
        return mark_safe(audio_tag)
    