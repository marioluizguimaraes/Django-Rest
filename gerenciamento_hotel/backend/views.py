from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from .models import ( Usuario, Quarto, TipoQuarto, Reserva,  ServicoAdicional, SolicitacaoServico, Avaliacao)
from .serializers import (QuartoSerializer, TipoQuartoSerializer, ReservaSerializer, ServicoAdicionalSerializer, SolicitacaoServicoSerializer, AvaliacaoSerializer, UsuarioRegistroSerializer)

class RegistroUsuarioView(CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            request.user.auth_token.delete()
            return Response(
                {"message": "Logout realizado com sucesso."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response( {"error": str(e)},status=status.HTTP_400_BAD_REQUEST)


class IsRecepcionistaOrGerente(IsAdminUser):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff or 
            request.user.tipo == 'Recepcionista' or 
            request.user.tipo == 'Gerente'
        )

class IsHospede(IsAuthenticated):

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.tipo == 'Hospede'
        )

class QuartoViewSet(viewsets.ModelViewSet):

    queryset = Quarto.objects.all().select_related('tipo_quarto')
    serializer_class = QuartoSerializer

    permission_classes = [IsRecepcionistaOrGerente]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo_quarto', 'status']
    search_fields = ['numero', 'tipo_quarto__nome']

    def get_permissions(self):

        if self.action in ['list', 'retrieve', 'disponibilidade']:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):

        queryset = super().get_queryset()
        capacidade_minima = self.request.query_params.get('capacidade_minima')
        if capacidade_minima:
            try:
                queryset = queryset.filter(
                    tipo_quarto__capacidade__gte=int(capacidade_minima)
                )
            except ValueError:
                pass
        
        return queryset

    @action(detail=False, methods=['get'])
    def disponibilidade(self, request):

        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        quartos_disponiveis = Quarto.objects.filter(
            status__in=['Disponivel', 'Limpeza']
        )
        
        quartos_ocupados_ids = Reserva.objects.filter(
            status__in=['Confirmada', 'Checkin', 'Pendente'],
            data_checkin__lt=data_fim,
            data_checkout__gt=data_inicio
        ).values_list('quarto_id', flat=True)
        
        queryset = quartos_disponiveis.exclude(
            id__in=quartos_ocupados_ids
        )

        queryset = self.filter_queryset(queryset) 

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReservaViewSet(viewsets.ModelViewSet):

    queryset = Reserva.objects.all().select_related('hospede', 'quarto__tipo_quarto')
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated] 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['hospede', 'status', 'quarto']
    search_fields = ['hospede__username', 'quarto__numero']

    def get_queryset(self):

        user = self.request.user
        
        if user.tipo == 'Hospede':
            return self.queryset.filter(hospede=user)
        
        if user.tipo in ['Recepcionista', 'Gerente'] or user.is_staff:
            return self.queryset.all()
        
        return self.queryset.none()

    def perform_create(self, serializer):

        if self.request.user.tipo != 'Hospede':
            raise serializers.ValidationError(
                "Apenas usuários do tipo 'Hóspede' podem criar reservas."
            )
        serializer.save(hospede=self.request.user, status='Pendente')

    @action(detail=True, methods=['post'], permission_classes=[IsRecepcionistaOrGerente])
    def fazer_checkin(self, request, pk=None):

        reserva = self.get_object()

        if reserva.status != 'Confirmada':
            return Response( {'error': 'Check-in só pode ser feito para reservas "Confirmadas".'},status=status.HTTP_400_BAD_REQUEST )

        if reserva.data_checkin != timezone.now().date():
            return Response( {'error': f'Check-in só pode ser feito na data de check-in ({reserva.data_checkin}).'},status=status.HTTP_400_BAD_REQUEST )

        reserva.status = 'Checkin'
        reserva.quarto.status = 'Ocupado'
        reserva.quarto.save()
        reserva.save()
        
        return Response(
            {'status': 'Check-in realizado com sucesso! Quarto atualizado para Ocupado.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsRecepcionistaOrGerente])
    def fazer_checkout(self, request, pk=None):

        reserva = self.get_object()
        
        if reserva.status != 'Checkin':
             return Response(
                {'error': 'Check-out só pode ser feito para reservas com "Check-in" realizado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reserva.status = 'Checkout'
        reserva.quarto.status = 'Limpeza'
        reserva.quarto.save()
        reserva.save()
        
        return Response(
            {'status': 'Check-out realizado com sucesso! Quarto atualizado para Limpeza.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancelar(self, request, pk=None):

        reserva = self.get_object()
        user = request.user

        if reserva.hospede != user and not IsRecepcionistaOrGerente().has_permission(request, self):
            return Response(
                {'error': 'Você não tem permissão para cancelar esta reserva.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if reserva.status not in ['Pendente', 'Confirmada']:
            return Response(
                {'error': f'Não é possível cancelar uma reserva com status "{reserva.status}".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        dias_para_checkin = (reserva.data_checkin - timezone.now().date()).days
        
        if dias_para_checkin < 2:
            reserva.valor_reembolso = reserva.valor_total * 0.50
            msg = f'Reserva cancelada com menos de 48h. Reembolso: R$ {reserva.valor_reembolso}'
        else: 
            reserva.valor_reembolso = reserva.valor_total * 1.00
            msg = f'Reserva cancelada com mais de 48h. Reembolso: R$ {reserva.valor_reembolso}'
        
        reserva.status = 'Cancelada'
        reserva.save()
        
        return Response({'status': msg}, status=status.HTTP_200_OK)


class SolicitacaoServicoViewSet(viewsets.ModelViewSet):

    queryset = SolicitacaoServico.objects.all().select_related('reserva', 'servico')
    serializer_class = SolicitacaoServicoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        
        if user.tipo == 'Hospede':
            return self.queryset.filter(reserva__hospede=user)
        
        if user.tipo in ['Recepcionista', 'Gerente'] or user.is_staff:
            reserva_id = self.request.query_params.get('reserva_id')
            if reserva_id:
                return self.queryset.filter(reserva_id=reserva_id)
            return self.queryset.all()
        
        return self.queryset.none()
    
    def get_permissions(self):

        if self.action in ['update', 'partial_update']:
            return [IsRecepcionistaOrGerente()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        reserva = serializer.validated_data.get('reserva')
        
        if self.request.user.tipo == 'Hospede':
            if reserva.hospede != self.request.user:
                raise serializers.ValidationError(
                    "Você só pode solicitar serviços para suas próprias reservas."
                )

        if reserva.status not in ['Confirmada', 'Checkin']:
            raise serializers.ValidationError(
                "Serviços só podem ser solicitados para reservas 'Confirmadas' ou 'Checkin'."
            )
            
        serializer.save()

class TipoQuartoViewSet(viewsets.ModelViewSet):
    queryset = TipoQuarto.objects.all()
    serializer_class = TipoQuartoSerializer
    permission_classes = [IsRecepcionistaOrGerente]

class ServicoAdicionalViewSet(viewsets.ModelViewSet):
    queryset = ServicoAdicional.objects.all()
    serializer_class = ServicoAdicionalSerializer
    permission_classes = [IsRecepcionistaOrGerente]

class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all().select_related('reserva', 'hospede')
    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.tipo == 'Hospede':
            return self.queryset.filter(hospede=user)
        if user.tipo in ['Recepcionista', 'Gerente'] or user.is_staff:
            return self.queryset.all()
        return self.queryset.none()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsRecepcionistaOrGerente()]
        return super().get_permissions()

    def perform_create(self, serializer):
        reserva = serializer.validated_data.get('reserva')
        
        if reserva.hospede != self.request.user:
            raise serializers.ValidationError( "Você só pode avaliar reservas que estão em seu nome.")

        serializer.save(hospede=self.request.user)