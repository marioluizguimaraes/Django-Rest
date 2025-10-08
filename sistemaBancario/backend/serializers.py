from rest_framework import serializers
from .models import Agencia, Cliente, Conta, Deposito, Saque, Transferencia

class AgenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agencia
        fields = '__all__' 

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__' 

class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = '__all__' 
        
class DepositoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposito
        fields = '__all__' 


class SaqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saque
        fields = '__all__' 

class TransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transferencia
        fields = '__all__' 