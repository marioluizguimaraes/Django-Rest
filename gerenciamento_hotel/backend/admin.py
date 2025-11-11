from django.contrib import admin
from .models import ( Usuario,  TipoQuarto,  Quarto,  Reserva,  ServicoAdicional,  SolicitacaoServico,  Avaliacao)

admin.site.register(Usuario)
admin.site.register(TipoQuarto)
admin.site.register(Quarto)
admin.site.register(Reserva)
admin.site.register(ServicoAdicional)
admin.site.register(SolicitacaoServico)
admin.site.register(Avaliacao)