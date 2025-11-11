from rest_framework import viewsets
from ..models import Coluna
from ..serializers import ColunaSerializer


class ColunaViewSet(viewsets.ModelViewSet):
    queryset = Coluna.objects.all()
    serializer_class = ColunaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        projeto_id = self.request.query_params.get('projeto')
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)
        return queryset
