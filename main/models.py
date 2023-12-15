import io
import re
from gtts import gTTS
from django.db import models


class Text_to_speech(models.Model):
    text = models.CharField(
        max_length=700,
        verbose_name="Текст",
        help_text="Введите текст, который вы хотите преобразовать в речь.",
    )
    file_name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Имя файла",
        help_text="Укажите имя аудиофайла.",
    )
    path_file = models.FileField(
        upload_to="voice/",
        verbose_name="Путь к файлу",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Дата и время создания записи.",
    )
    
    def save(self, *args, **kwargs):
        # Проверяем наличие кириллических символов в тексте с использованием регулярного выражения
        match = re.search(r"[\u0400-\u04ff]|[\u0500-\u052f]", self.text)
        
        # Определяем язык на основе наличия кириллических символов
        lang = "ru" if match else "en"
        
        # Создаем объект gTTS (Google Text-to-Speech) с текстом и языком
        tts = gTTS(text=self.text, lang=lang)
        
        # Создаем объект BytesIO для сохранения сгенерированного голоса в виде байтов
        voice_bytes = io.BytesIO()
        
        # Записываем сгенерированный голос в объект BytesIO
        tts.write_to_fp(voice_bytes)
        
        # Переходим в начало объекта BytesIO
        voice_bytes.seek(0)
        
        self.path_file.name = f"voice/{self.file_name}.wav"
        
        with open(self.path_file.path, "wb") as f:
            f.write(voice_bytes.read())

        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = "Текст в речь"
        verbose_name_plural = "Тексты в речь"
