from rest_framework import serializers
from django.utils import timezone
from .models import ( Usuario, TipoQuarto, Quarto, Reserva,  ServicoAdicional, SolicitacaoServico, Avaliacao)
from rest_framework.authtoken.models import Token

class UsuarioRegistroSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'tipo']
        extra_kwargs = {
            'password': {'write_only': True} 
        }

    def create(self, validated_data):

        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            tipo=validated_data.get('tipo', 'Hospede')
        )

        Token.objects.create(user=user)
        return user

class TipoQuartoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoQuarto
        fields = '__all__' 

class QuartoSerializer(serializers.ModelSerializer):

    tipo_quarto = TipoQuartoSerializer(read_only=True)

    tipo_quarto_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoQuarto.objects.all(),
        source='tipo_quarto',
        write_only=True,
        label='ID do Tipo de Quarto'
    )

    class Meta:
        model = Quarto
        fields = [
            'id', 'numero', 'andar', 'status', 
            'tipo_quarto', 'tipo_quarto_id'
        ]


class ServicoAdicionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServicoAdicional
        fields = '__all__'

class ReservaSerializer(serializers.ModelSerializer):
   
    hospede = serializers.StringRelatedField(read_only=True)
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)
    quarto_info = QuartoSerializer(source='quarto', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'hospede', 'quarto', 'quarto_info', 'data_checkin', 'data_checkout',
            'num_hospedes', 'valor_total', 'status', 'data_reserva'
        ]
        extra_kwargs = {

            'quarto': {'write_only': True} 
        }

    def validate_data_checkin(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError('A data de check-in não pode ser no passado.')
        return value

    def validate(self, data):
        data_checkin = data.get('data_checkin', getattr(self.instance, 'data_checkin', None))
        data_checkout = data.get('data_checkout', getattr(self.instance, 'data_checkout', None))
        num_hospedes = data.get('num_hospedes', getattr(self.instance, 'num_hospedes', None))
        quarto = data.get('quarto', getattr(self.instance, 'quarto', None))

        if data_checkin and data_checkout and data_checkout <= data_checkin:
            raise serializers.ValidationError('A data de check-out deve ser posterior à data de check-in.')

        if num_hospedes and quarto:
            if num_hospedes > quarto.tipo_quarto.capacidade:
                raise serializers.ValidationError(
                    f'O número de hóspedes ({num_hospedes}) excede a capacidade do quarto ({quarto.tipo_quarto.capacidade}).'
                )

        if quarto and data_checkin and data_checkout:
            if quarto.status == 'Manutencao':

                if self.instance is None or self.instance.quarto != quarto:
                    raise serializers.ValidationError('Não é possível reservar um quarto em manutenção.')

            reservas_conflitantes = Reserva.objects.filter(
                quarto=quarto,
                status__in=['Confirmada', 'Checkin', 'Pendente']).filter( data_checkin__lt=data_checkout,  data_checkout__gt=data_checkin )
            
            if self.instance:
                reservas_conflitantes = reservas_conflitantes.exclude(pk=self.instance.pk)
            
            if reservas_conflitantes.exists():
                raise serializers.ValidationError(f'O Quarto {quarto.numero} já está reservado neste período.')

        return data

class SolicitacaoServicoSerializer(serializers.ModelSerializer):

    reserva_info = serializers.StringRelatedField(source='reserva', read_only=True)
    servico_info = ServicoAdicionalSerializer(source='servico', read_only=True)
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SolicitacaoServico
        fields = [
            'id', 'reserva', 'reserva_info', 'servico', 'servico_info', 
            'quantidade', 'status', 'status_display', 'data_solicitacao', 'valor_total'
        ]
        read_only_fields = ('data_solicitacao', 'valor_total')
        extra_kwargs = {
            'reserva': {'write_only': True},
            'servico': {'write_only': True}
        }


class AvaliacaoSerializer(serializers.ModelSerializer):

    hospede = serializers.StringRelatedField(read_only=True)
    reserva_info = serializers.StringRelatedField(source='reserva', read_only=True)

    class Meta:
        model = Avaliacao
        fields = [
            'id', 'reserva', 'reserva_info', 'hospede', 
            'nota', 'comentario', 'data_avaliacao'
        ]
        read_only_fields = ('data_avaliacao',)
        extra_kwargs = {
            'reserva': {'write_only': True}
        }

    def validate_reserva(self, value):
        if value.status != 'Checkout':
            raise serializers.ValidationError('A avaliação só pode ser feita após o checkout da reserva.')
        return value