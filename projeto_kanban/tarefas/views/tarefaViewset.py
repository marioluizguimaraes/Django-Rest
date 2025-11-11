from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from ..models import Tarefa
from ..serializers import TarefaSerializer

class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.all().select_related('responsavel', 'coluna')
    serializer_class = TarefaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        prioridade = self.request.query_params.get('prioridade')
        coluna = self.request.query_params.get('coluna')

        if prioridade:
            queryset = queryset.filter(prioridade=prioridade)
        if coluna:
            queryset = queryset.filter(coluna_id=coluna)

        return queryset

    @action(detail=True, methods=['post'])
    def atribuir(self, request, pk=None):
        tarefa = self.get_object()
        user_id = request.data.get("user_id")

        try:
            usuario = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        tarefa.responsavel = usuario
        tarefa.save()

        return Response({"detail": f"Tarefa atribuída a {usuario.username} com sucesso!"}, status=status.HTTP_200_OK)
