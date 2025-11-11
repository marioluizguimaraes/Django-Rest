from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime

class Usuario(AbstractUser):

    TIPO_CHOICES = [
        ('Hospede', 'Hóspede'),
        ('Recepcionista', 'Recepcionista'),
        ('Gerente', 'Gerente'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='Hospede',
        help_text='Tipo de usuário no sistema'
    )
    cpf = models.CharField(
        max_length=14, 
        unique=True, 
        null=True, 
        blank=True,
        help_text='CPF no formato XXX.XXX.XXX-XX'
    )
    telefone = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        help_text='Telefone com DDD, ex: (XX) 9XXXX-XXXX'
    )
    data_nascimento = models.DateField(
        null=True, 
        blank=True,
        help_text='Data de nascimento no formato AAAA-MM-DD'
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"


class TipoQuarto(models.Model):

    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    preco_diaria = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Preço da diária para este tipo de quarto'
    )
    capacidade = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Número máximo de hóspedes que o quarto suporta'
    )

    class Meta:
        verbose_name = 'Tipo de Quarto'
        verbose_name_plural = 'Tipos de Quarto'

    def __str__(self):
        return f"{self.nome} (Cap: {self.capacidade} - R$ {self.preco_diaria})"


class Quarto(models.Model):

    STATUS_CHOICES = [
        ('Disponivel', 'Disponível'),
        ('Ocupado', 'Ocupado'),
        ('Manutencao', 'Em Manutenção'),
        ('Limpeza', 'Em Limpeza'),
    ]
    
    numero = models.CharField(
        max_length=10, 
        unique=True,
        help_text='Número ou identificador do quarto (ex: 101, 203A)'
    )
    andar = models.IntegerField(default=1)
    tipo_quarto = models.ForeignKey(
        TipoQuarto,
        on_delete=models.PROTECT,
        related_name='quartos'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Disponivel'
    )

    class Meta:
        verbose_name = 'Quarto'
        verbose_name_plural = 'Quartos'
        ordering = ['numero']

    def __str__(self):
        return f"Quarto {self.numero} ({self.tipo_quarto.nome}) - {self.get_status_display()}"

class Reserva(models.Model):

    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Confirmada', 'Confirmada'),
        ('Checkin', 'Check-in Realizado'),
        ('Checkout', 'Checkout Realizado'),
        ('Cancelada', 'Cancelada'),
    ]

    hospede = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reservas',
        limit_choices_to={'tipo': 'Hospede'} 
    )
    quarto = models.ForeignKey(
        Quarto,
        on_delete=models.PROTECT,
        related_name='reservas'
    )
    data_checkin = models.DateField(help_text='Data de entrada')
    data_checkout = models.DateField(help_text='Data de saída')
    num_hospedes = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Número total de hóspedes na reserva'
    )
    valor_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text='Valor total calculado da estadia (diárias * preço)'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pendente'
    )
    data_reserva = models.DateTimeField(auto_now_add=True)

    valor_reembolso = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Valor a ser reembolsado em caso de cancelamento'
    )

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"Reserva {self.id} - {self.hospede.username} - Quarto {self.quarto.numero}"

    def clean(self):

        if self.data_checkin and self.data_checkin < timezone.now().date():
            raise ValidationError('A data de check-in não pode ser no passado.')
        
        if self.data_checkin and self.data_checkout and self.data_checkout <= self.data_checkin:
            raise ValidationError('A data de check-out deve ser posterior à data de check-in.')
        
        if self.num_hospedes and self.quarto and self.num_hospedes > self.quarto.tipo_quarto.capacidade:
            raise ValidationError(f'O número de hóspedes ({self.num_hospedes}) excede a capacidade do quarto ({self.quarto.tipo_quarto.capacidade}).')
        
        if self.quarto and self.data_checkin and self.data_checkout:
            if self.quarto.status == 'Manutencao':
                raise ValidationError('Não é possível reservar um quarto em manutenção.')
            
            reservas_conflitantes = Reserva.objects.filter(
                quarto=self.quarto,
                status__in=['Confirmada', 'Checkin', 'Pendente']
            ).exclude(pk=self.pk).filter( data_checkin__lt=self.data_checkout, data_checkout__gt=self.data_checkin)
        
            if reservas_conflitantes.exists():
                raise ValidationError(f'O Quarto {self.quarto.numero} já está reservado neste período.')

    def save(self, *args, **kwargs):
        if self.data_checkin and self.data_checkout and self.quarto:
            duracao = (self.data_checkout - self.data_checkin).days
            if duracao <= 0:
                duracao = 1
            self.valor_total = duracao * self.quarto.tipo_quarto.preco_diaria
            
        super().clean()
        super().save(*args, **kwargs)


class ServicoAdicional(models.Model):

    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Serviço Adicional'
        verbose_name_plural = 'Serviços Adicionais'

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"


class SolicitacaoServico(models.Model):

    STATUS_CHOICES = [
        ('Solicitado', 'Solicitado'),
        ('Em_Andamento', 'Em Andamento'),
        ('Concluido', 'Concluído'),
        ('Cancelado', 'Cancelado'),
    ]
    
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='servicos_solicitados'
    )
    servico = models.ForeignKey(
        ServicoAdicional,
        on_delete=models.PROTECT,
        related_name='solicitacoes'
    )
    quantidade = models.IntegerField(
        default=1, 
        validators=[MinValueValidator(1)]
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Solicitado'
    )
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, help_text='Valor total (serviço * quantidade)')

    class Meta:
        verbose_name = 'Solicitação de Serviço'
        verbose_name_plural = 'Solicitações de Serviços'

    def __str__(self):
        return f"{self.quantidade}x {self.servico.nome} (Reserva {self.reserva.id})"

    def save(self, *args, **kwargs):

        if self.servico and self.quantidade:
            self.valor_total = self.servico.preco * self.quantidade
        super().save(*args, **kwargs)


class Avaliacao(models.Model):

    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.CASCADE,
        related_name='avaliacao'
    )
    hospede = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        related_name='avaliacoes_feitas'
    )
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Nota de 1 a 5 estrelas'
    )
    comentario = models.TextField(blank=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ('reserva', 'hospede') 

    def __str__(self):
        return f"Avaliação da Reserva {self.reserva.id} - Nota {self.nota}"
    
    def clean(self):
        if self.reserva and self.reserva.status != 'Checkout':
            raise ValidationError('A avaliação só pode ser feita após o checkout da reserva.')
        
        if self.reserva and self.hospede != self.reserva.hospede:
            raise ValidationError('A avaliação deve ser feita pelo hóspede da reserva.')