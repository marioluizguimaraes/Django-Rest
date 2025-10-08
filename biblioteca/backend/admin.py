from django.contrib import admin
from .models import Livro, Categoria, Editora, Autor, Usuario, Emprestimo, Multa, Reserva

admin.site.register(Livro)
admin.site.register(Categoria)
admin.site.register(Editora)

admin.site.register(Autor)
admin.site.register(Usuario)

admin.site.register(Emprestimo)
admin.site.register(Multa)
admin.site.register(Reserva)
