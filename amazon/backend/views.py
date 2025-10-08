from django.shortcuts import render
from rest_framework import viewsets
from .models import Cliente
from .serializers import ClienteSerializer

#O ModelViewSet fornece ações CRUD (Create, Retrieve, Update, Delete) para um modelo específico. 
class ClienteViewSet(viewsets.ModelViewSet):
    #O queryset define a consulta que será usada para recuperar os objetos do banco de dados.
    queryset = Cliente.objects.all()
    
    #O serializer_class define o serializer que será usado para serializar os objetos recuperados do banco de dados.
    serializer_class = ClienteSerializer 