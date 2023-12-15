import io
import re

from gtts import gTTS
from django.utils import timezone
from django.http import FileResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions, status, serializers
from rest_framework.authtoken.views import ObtainAuthToken

from .models import Text_to_speech
from .serializers import TextToSpeechSerializer, UserSerializer


MIN_TEXT_LENGTH = 10
MAX_TEXT_LENGTH = 700
MIN_FILE_NAME_LENGTH = 5
MAX_FILE_NAME_LENGTH = 20


class BaseTextToSpeechView(generics.GenericAPIView):
    queryset = Text_to_speech.objects.all()
    serializer_class = TextToSpeechSerializer
    permission_classes = [permissions.IsAuthenticated]

    def validate_request_data(self, text, file_name):
        if not text:
            raise serializers.ValidationError({"error": "Текст не может быть пустым."})

        elif len(text) < MIN_TEXT_LENGTH:
            raise serializers.ValidationError(
                {"error": f"Текст не может быть меньше {MIN_TEXT_LENGTH} символов."}
            )
        elif not file_name:
            raise serializers.ValidationError(
                {"error": "Имя файла не может быть пустым."}
            )
        elif len(file_name) < MIN_FILE_NAME_LENGTH:
            raise serializers.ValidationError(
                {
                    "error": f"Имя файла не может быть меньше {MIN_FILE_NAME_LENGTH} символов."
                }
            )
        elif len(text) > MAX_TEXT_LENGTH:
            raise serializers.ValidationError(
                {"error": f"Текст не может быть больше {MAX_TEXT_LENGTH} символов."}
            )
        elif len(file_name) > MAX_FILE_NAME_LENGTH:
            raise serializers.ValidationError(
                {
                    "error": f"Имя файла не может быть больше {MAX_FILE_NAME_LENGTH} символов."
                }
            )


class TextToSpeechView(BaseTextToSpeechView, generics.ListCreateAPIView):
    def post(self, request, *args, **kwargs):
        text = request.data.get("text")
        file_name = request.data.get("file_name")
        self.validate_request_data(text, file_name)
        
        text_to_speech = Text_to_speech.objects.create(
            text=text,
            file_name=file_name
        )
        text_to_speech.save()
        
        serializer = TextToSpeechSerializer(text_to_speech)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class TextToSpeechDetailView(BaseTextToSpeechView, 
    generics.RetrieveUpdateDestroyAPIView):
    
    def get(self, request, *args, **kwargs):
        text_to_speech = get_object_or_404(Text_to_speech, id=kwargs.get("id"))
        serializer = TextToSpeechSerializer(text_to_speech)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        text = request.data.get("text")
        file_name = request.data.get("file_name")
        self.validate_request_data(text, file_name)
        
        text_to_speech = Text_to_speech.objects.get(id=kwargs.get("id"))
        text_to_speech.text = text
        text_to_speech.file_name = file_name
        text_to_speech.save()
        
        serializer = TextToSpeechSerializer(text_to_speech)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        text_to_speech = Text_to_speech.objects.get(id=kwargs.get("id"))
        text_to_speech.delete()
        return Response("Delete success True", status=status.HTTP_204_NO_CONTENT)

    
class DownloadVoiceView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, id, *args, **kwargs):

        text_to_speech = get_object_or_404(Text_to_speech, id=id)

        response = FileResponse(open(text_to_speech.path_file, "rb"))
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{text_to_speech.file_name}.wav"'
        return response