from django.db import models

class Coluna(models.Model):
    titulo = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    projeto = models.ForeignKey('tarefas.Projeto', on_delete=models.CASCADE, related_name='colunas')
    def __str__(self):
        return f"{self.titulo}"
