from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    data_cadastro = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
            return f'{self.nome} - {self.email}'
    
    # Define o nome exato da tabela no banco de dados
    class Meta:
        db_table = 'cliente'