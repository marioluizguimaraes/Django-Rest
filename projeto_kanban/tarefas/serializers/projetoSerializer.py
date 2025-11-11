from rest_framework import serializers
from ..models import Projeto
from .colunaSerializer import ColunaSerializer

class ProjetoSerializer(serializers.ModelSerializer):
    colunas = ColunaSerializer(many=True, read_only=True)
    membros = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='username'
    )
    total_tarefas = serializers.SerializerMethodField()

    class Meta:
        model = Projeto
        fields = [
            'id',
            'nome',
            'descricao',
            'data_criacao',
            'proprietario',
            'membros',
            'colunas',
            'total_tarefas',
        ]

    def get_total_tarefas(self, obj):
        return sum(coluna.tarefas.count() for coluna in obj.colunas.all())
