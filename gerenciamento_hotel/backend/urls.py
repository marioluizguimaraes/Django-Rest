from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'quartos', views.QuartoViewSet)
router.register(r'reservas', views.ReservaViewSet)
router.register(r'solicitacoes-servico', views.SolicitacaoServicoViewSet)
router.register(r'tipos-quarto', views.TipoQuartoViewSet)
router.register(r'servicos-adicionais', views.ServicoAdicionalViewSet)
router.register(r'avaliacoes', views.AvaliacaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', obtain_auth_token, name='api_token_auth'),
    path('auth/registro/', views.RegistroUsuarioView.as_view(), name='auth_registro'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
]