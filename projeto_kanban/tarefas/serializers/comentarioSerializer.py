from rest_framework import serializers
from ..models import Comentario

class ComentarioSerializer(serializers.ModelSerializer):
    autor_nome = serializers.CharField(source='autor.username', read_only=True)

    class Meta:
        model = Comentario
        fields = [
            'id',
            'autor',
            'autor_nome',
            'texto',
            'data_criacao',
        ]
