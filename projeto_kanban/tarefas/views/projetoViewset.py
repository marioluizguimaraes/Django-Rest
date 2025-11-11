from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from ..models import Projeto, Tarefa
from ..serializers import ProjetoSerializer, TarefaSerializer


class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer

    @action(detail=True, methods=['post'])
    def add_membro(self, request, pk=None):
        projeto = self.get_object()
        user_id = request.data.get("user_id")

        try:
            usuario = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        projeto.membros.add(usuario)
        projeto.save()

        return Response({"detail": f"Usuário '{usuario.username}' adicionado com sucesso!"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def minhas_tarefas(self, request, pk=None):
        projeto = self.get_object()
        usuario = request.user

        tarefas = Tarefa.objects.filter(
            coluna__projeto=projeto,
            responsavel=usuario
        )

        serializer = TarefaSerializer(tarefas, many=True)
        return Response(serializer.data)
