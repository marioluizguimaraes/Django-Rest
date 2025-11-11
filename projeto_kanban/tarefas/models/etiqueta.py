from django.db import models

class Etiqueta(models.Model):
    nome = models.CharField(max_length=50)
    cor = models.CharField(max_length=7, help_text="Código hexadecimal da cor, ex: #FF5733")

    def __str__(self):
        return self.nome
