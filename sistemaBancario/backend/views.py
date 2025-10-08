from django.shortcuts import render
from rest_framework import viewsets
from .models import Agencia, Cliente, Conta, Deposito, Saque, Transferencia

from .serializers import AgenciaSerializer, ClienteSerializer, ContaSerializer, DepositoSerializer, SaqueSerializer, TransferenciaSerializer

class AgenciaViewSet(viewsets.ModelViewSet):
    queryset = Agencia.objects.all()
    serializer_class = AgenciaSerializer 

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer 

class ContaViewSet(viewsets.ModelViewSet):
    queryset = Conta.objects.all()
    serializer_class = ContaSerializer 

class DepositoViewSet(viewsets.ModelViewSet):
    queryset = Deposito.objects.all()
    serializer_class = DepositoSerializer 

class SaqueViewSet(viewsets.ModelViewSet):
    queryset = Saque.objects.all()
    serializer_class = SaqueSerializer 

class TransferenciaViewSet(viewsets.ModelViewSet):
    queryset = Transferencia.objects.all()
    serializer_class = TransferenciaSerializer 
