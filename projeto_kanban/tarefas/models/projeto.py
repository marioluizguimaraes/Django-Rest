from django.db import models
from django.contrib.auth.models import User

class Projeto(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projetos_proprios')
    membros = models.ManyToManyField(User, related_name='projetos_membro', blank=True)

    def __str__(self):
        return self.nome
