from rest_framework.routers import DefaultRouter
from .views import ProjetoViewSet, ColunaViewSet, TarefaViewSet, ComentarioViewSet, EtiquetaViewSet

router = DefaultRouter()
router.register(r'projetos', ProjetoViewSet)
router.register(r'colunas', ColunaViewSet)
router.register(r'tarefas', TarefaViewSet)
router.register(r'comentarios', ComentarioViewSet)
router.register(r'etiquetas', EtiquetaViewSet)

urlpatterns = router.urls
