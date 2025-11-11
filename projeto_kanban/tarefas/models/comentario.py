from django.db import models
from django.contrib.auth.models import User

class Comentario(models.Model):
    tarefa = models.ForeignKey('tarefas.Tarefa', on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentário de {self.autor.username}"
