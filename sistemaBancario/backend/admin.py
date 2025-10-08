from django.contrib import admin
from .models import Agencia, Cliente, Conta, Deposito, Saque, Transferencia

admin.site.register(Agencia)
admin.site.register(Cliente)
admin.site.register(Conta)
admin.site.register(Deposito)
admin.site.register(Saque)
admin.site.register(Transferencia)