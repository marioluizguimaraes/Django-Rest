from rest_framework import viewsets
from .models import Livro, Categoria, Editora, Autor, Usuario, Emprestimo, Multa, Reserva
from .serializers import (
    LivroSerializer, CategoriaSerializer, EditoraSerializer, 
    AutorSerializer, UsuarioSerializer, EmprestimoSerializer, 
    MultaSerializer, ReservaSerializer
)

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class EditoraViewSet(viewsets.ModelViewSet):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer


class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer


class MultaViewSet(viewsets.ModelViewSet):
    queryset = Multa.objects.all()
    serializer_class = MultaSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
