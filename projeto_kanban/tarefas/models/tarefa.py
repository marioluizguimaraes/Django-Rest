from django.db import models
from django.contrib.auth.models import User

class Tarefa(models.Model):
    PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]

    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    coluna = models.ForeignKey('tarefas.Coluna', on_delete=models.CASCADE, related_name='tarefas')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tarefas_responsavel')
    criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tarefas_criadas')
    prioridade = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField('tarefas.Etiqueta', blank=True, related_name='tarefas')

    def __str__(self):
        return self.titulo
