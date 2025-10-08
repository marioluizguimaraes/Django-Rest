from django.db import models

class Livro(models.Model):
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    ano_publicacao = models.PositiveIntegerField()
    genero = models.CharField(max_length=100)

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'livro'

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'categoria'

class Editora(models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'editora'


class Autor(models.Model):
    nome = models.CharField(max_length=255)
    data_nascimento = models.DateField()
    nacionalidade = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
    class Meta:
        db_table = 'autor'

class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    data_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'usuario'


class Emprestimo(models.Model):
    id_livro = models.PositiveIntegerField()
    id_usuario = models.PositiveIntegerField()
    data_emprestimo = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Empréstimo {self.id} - Livro {self.id_livro}"

    class Meta:
        db_table = 'emprestimo'

class Multa(models.Model):
    id_usuario = models.PositiveIntegerField()
    valor_multa = models.DecimalField(max_digits=6, decimal_places=2)
    data_pagamento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Multa Usuário {self.id_usuario} - R$ {self.valor_multa}"
    
    class Meta:
        db_table = 'multa'

class Reserva(models.Model):
    id_livro = models.PositiveIntegerField()
    id_usuario = models.PositiveIntegerField()
    data_reserva = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Reserva {self.id} - Livro {self.id_livro}"

    class Meta:
        db_table = 'reserva'
