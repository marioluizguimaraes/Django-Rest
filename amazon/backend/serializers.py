from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        # Se for necessário incluir apenas alguns campos, basta informar os campos desejados 
        # na lista fields, como por exemplo: fields = ['nome', 'email']. 
        fields = '__all__'