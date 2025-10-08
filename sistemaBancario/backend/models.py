from django.db import models

class Agencia(models.Model):

    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=150)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20, blank=True)
    gerente_responsavel = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=10, default="ativa")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    class Meta:
        db_table = "agencia"


class Cliente(models.Model):

    cpf = models.CharField(max_length=14, unique=True)
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField(null=True, blank=True)
    endereco = models.TextField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default="ativo")

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

    class Meta:
        db_table = "cliente"

class Conta(models.Model):

    numero = models.CharField(max_length=30, unique=True)
    codigo_agencia = models.CharField(max_length=20)
    cpf_titular = models.CharField(max_length=14)
    tipo = models.CharField(max_length=10,)
    saldo = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    data_abertura = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, default="ativa")
    limite_saque_diario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.numero} ({self.tipo})"

    class Meta:
        db_table = "conta"

class Deposito(models.Model):

    numero_conta = models.CharField(max_length=30)
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    data_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=12)
    descricao = models.TextField(blank=True)
    caixa_operador = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Depósito {self.valor} -> {self.numero_conta}"

    class Meta:
        db_table = "deposito"

class Saque(models.Model):

    numero_conta = models.CharField(max_length=30)
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    data_hora = models.DateTimeField(auto_now_add=True)
    local = models.CharField(max_length=20)
    caixa_operador = models.CharField(max_length=120, blank=True)
    status_operacao = models.CharField(max_length=10, default="aprovado")
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"Saque {self.valor} - {self.numero_conta} ({self.status_operacao})"

    class Meta:
        db_table = "saque"

class Transferencia(models.Model):

    conta_origem = models.CharField(max_length=30)
    conta_destino = models.CharField(max_length=30)
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    data_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=12)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=12, default="processando")
    operador = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Transf {self.valor} {self.conta_origem} -> {self.conta_destino} ({self.status})"

    class Meta:
        db_table = "transferencia"