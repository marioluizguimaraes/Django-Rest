from rest_framework import serializers
from ..models import Coluna
from .tarefaSerializer import TarefaSerializer

class ColunaSerializer(serializers.ModelSerializer):
    tarefas = TarefaSerializer(many=True, read_only=True)
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True)

    class Meta:
        model = Coluna
        fields = [
            'id',
            'titulo',
            'ordem',
            'projeto',
            'projeto_nome',
            'tarefas',
        ]
