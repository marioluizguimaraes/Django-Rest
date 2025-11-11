from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Tarefa
from .comentarioSerializer import ComentarioSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TarefaSerializer(serializers.ModelSerializer):
    responsavel = UsuarioSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='nome'
    )
    comentarios = ComentarioSerializer(many=True, read_only=True)
    total_comentarios = serializers.SerializerMethodField()

    class Meta:
        model = Tarefa
        fields = [
            'id',
            'titulo',
            'descricao',
            'coluna',
            'responsavel',
            'criador',
            'prioridade',
            'data_criacao',
            'data_conclusao',
            'tags',
            'comentarios',
            'total_comentarios',
        ]

    def get_total_comentarios(self, obj):
        return obj.comentarios.count()
