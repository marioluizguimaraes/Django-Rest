# Autenticação com Django REST Framework (DRF)

Este guia resume os conceitos e o fluxo de implementação de autenticação baseada em Token no DRF, com base nos projetos que desenvolvemos (Gerenciador de Projetos, Sistema de Hotel).

## O Conceito Central: Autenticação por Token

APIs REST, por padrão, são "stateless" (sem estado). Isso significa que elas não "lembram" quem você é entre uma requisição e outra. Você não pode simplesmente "fazer login" e esperar que a API saiba quem você é na próxima vez.

Para resolver isso, usamos a **Autenticação por Token**.

### O Fluxo Básico

1.  **Login:** O cliente (seu CLI, Postman, etc.) envia um `username` e `password` para um endpoint de login **apenas uma vez**.
2.  **Receber Token:** A API valida essas credenciais. Se estiverem corretas, ela gera (ou busca) um "Token" (uma longa string de caracteres, ex: `e417633f5bf3...`) e o envia de volta para o cliente.
3.  **Salvar Token:** O cliente **salva** esse token localmente (por exemplo, em um arquivo `.token`, como sugerido na atividade).
4.  **Autenticar Requisições:** Para *todas* as futuras requisições (criar quarto, fazer reserva, etc.), o cliente anexa esse token no "cabeçalho" (Header) da requisição.
5.  **Validação:** A API vê o token no cabeçalho, verifica em seu banco de dados a quem ele pertence e pensa: "Ah, esta requisição é do usuário 'mario'".
6.  **Logout:** O cliente envia seu token para um endpoint de logout. A API recebe, identifica o usuário e **apaga o token** do banco de dados, invalidando-o. O cliente então apaga o token local.

---

## Parte 1: Configurando o Backend (Django)

### 1. Instalação e Configuração (`settings.py`)

Primeiro, precisamos dizer ao Django para usar a autenticação por token.

```python
# gerenciamento_hotel/settings.py

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework.authtoken',  # <-- PASSO 1: Adiciona o app de token
    'backend',
    # ...
]

# Configuração global do DRF
REST_FRAMEWORK = {
    # PASSO 2: Define TokenAuthentication como o método de autenticação padrão
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    # PASSO 3: Define que, POR PADRÃO, todos os endpoints exigem login
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# PASSO 4: Informa ao Django para usar nosso modelo de usuário customizado
AUTH_USER_MODEL = 'backend.Usuario'

### 2\. Aplicar Migrações

Depois de adicionar `rest_framework.authtoken`, você **DEVE** rodar as migrações.

```bash
python manage.py migrate
```

  * **Erro Comum:** Se você esquecer este passo, você receberá o erro `ERRO: relação "authtoken_token" não existe` ao tentar fazer login, pois a tabela de tokens não foi criada no banco.

### 3\. Endpoints de Autenticação (`urls.py` e `views.py`)

Precisamos de três endpoints: Login, Registro e Logout.

#### Login (O Padrão do DRF)

O DRF já nos dá uma view pronta para o login (`obtain_auth_token`).

```python
# gerenciamento_hotel/backend/urls.py

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # ...
    # POST para esta URL com 'username' e 'password' retorna o token
    path('auth/login/', obtain_auth_token, name='api_token_auth'),
    # ...
]
```

#### Registro (Customizado)

Precisamos de um endpoint público (`AllowAny`) para criar usuários.

```python
# gerenciamento_hotel/backend/serializers.py

from rest_framework.authtoken.models import Token

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'email', 'tipo'] # Campos do formulário
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Cria o usuário com a senha criptografada
        user = Usuario.objects.create_user(**validated_data)
        # CRIA O TOKEN JUNTO COM O USUÁRIO
        Token.objects.create(user=user)
        return user

# gerenciamento_hotel/backend/views.py

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny # Importar!

class RegistroUsuarioView(CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioRegistroSerializer
    # Sobrescreve o padrão global (IsAuthenticated)
    # para permitir que qualquer um se registre
    permission_classes = [AllowAny]

# gerenciamento_hotel/backend/urls.py

urlpatterns = [
    # ...
    path('auth/registro/', views.RegistroUsuarioView.as_view(), name='auth_registro'),
    # ...
]
```

#### Logout (Customizado)

Precisamos de um endpoint protegido (`IsAuthenticated`) que delete o token.

```python
# gerenciamento_hotel/backend/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class LogoutView(APIView):
    # Exige que o usuário esteja autenticado para fazer logout
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Pega o token do usuário que fez a requisição e o deleta
            request.user.auth_token.delete()
            return Response(
                {"message": "Logout realizado com sucesso."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# gerenciamento_hotel/backend/urls.py

urlpatterns = [
    # ...
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
    # ...
]
```

-----

## Parte 2: Permissões (Controlando o Acesso)

Ter um token é o primeiro passo (Autenticação). Saber o que você pode fazer com ele é o segundo (Autorização/Permissão).

### 1\. Padrão Global vs. Exceções

  * **Padrão Global (`settings.py`):** `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]`
      * **O que faz:** Fecha toda a API. Ninguém faz nada sem um token válido.
  * **Exceção (`views.py`):** `permission_classes = [AllowAny]`
      * **O que faz:** Abre um endpoint específico para o público (ex: Registro, Listagem de Quartos).

### 2\. Permissões por Tipo de Usuário

No projeto do hotel, tínhamos tipos de usuário (`Hospede`, `Recepcionista`, `Gerente`). Criamos classes de permissão customizadas:

```python
# gerenciamento_hotel/backend/views.py

class IsRecepcionistaOrGerente(IsAdminUser):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff or 
            request.user.tipo == 'Recepcionista' or 
            request.user.tipo == 'Gerente'
        )

# Como usar na ViewSet:
class TipoQuartoViewSet(viewsets.ModelViewSet):
    queryset = TipoQuarto.objects.all()
    serializer_class = TipoQuartoSerializer
    # Apenas staff pode criar/editar tipos de quarto
    permission_classes = [IsRecepcionistaOrGerente]
```

### 3\. Permissões por "Dono" do Objeto

Esta é a permissão mais comum: "Um usuário só pode ver/editar seus próprios dados".

Nós implementamos isso **sobrescrevendo o `get_queryset`** na ViewSet.

```python
# gerenciamento_hotel/backend/views.py

class ReservaViewSet(viewsets.ModelViewSet):
    # ...
    def get_queryset(self):
        user = self.request.user
        
        # Se for Hóspede, filtre as reservas para mostrar APENAS as dele
        if user.tipo == 'Hospede':
            return self.queryset.filter(hospede=user)
        
        # Se for Staff, mostre todas
        if user.tipo in ['Recepcionista', 'Gerente'] or user.is_staff:
            return self.queryset.all()
        
        return self.queryset.none() # Se não for nenhum, não mostre nada
```

-----

## Parte 3: Consumindo a API (O Cliente)

### O Erro Mais Comum: O Header `Authorization`

Quando o cliente (Postman, cURL, Python) envia o token, ele **DEVE** seguir um formato específico.

  * **ERRADO:** `Authorization: e417633f5bf3a1b5cbb0e24894fa1787b63e3957`
  * **CORRETO:** `Authorization: Token e417633f5bf3a1b5cbb0e24894fa1787b63e3957`

Você precisa **obrigatoriamente** incluir o prefixo ` Token  ` (com 'T' maiúsculo e um espaço) antes do token.

### Exemplo em Python (com `requests`)

```python
import requests

# 1. Fazer Login
response_login = requests.post(
    '[http://127.0.0.1:8000/api/auth/login/](http://127.0.0.1:8000/api/auth/login/)', 
    data={'username': 'gerente', 'password': '123'}
)
token = response_login.json().get('token')

# 2. Salvar o token (em um arquivo .token, por exemplo)
with open('.token', 'w') as f:
    f.write(token)

# 3. Usar o token para uma requisição protegida
token_lido = open('.token', 'r').read().strip()
headers = {
    'Authorization': f'Token {token_lido}' # <-- O formato correto!
}

response_quartos = requests.get(
    '[http://127.0.0.1:8000/api/quartos/](http://127.0.0.1:8000/api/quartos/)', 
    headers=headers
)
print(response_quartos.json())
```

### Erros Comuns e o Que Significam

  * **ERRO 401 (Não Autorizado):**
      * *Mensagem:* `"detail": "Autenticação não fornecida."`
      * *Causa:* Você não enviou o header `Authorization`.
      * *Mensagem:* `"detail": "Token inválido."`
      * *Causa:* O formato do header está errado (ex: esqueceu o prefixo ` Token  `) ou o token em si está incorreto/expirado.
  * **ERRO 403 (Proibido):**
      * *Mensagem:* `"detail": "Você não tem permissão para executar esta ação."`
      * *Causa:* Você **ESTÁ** autenticado (seu token é válido), mas o seu tipo de usuário (ex: "Hospede") não tem permissão para acessar aquele recurso (ex: criar um `TipoQuarto`, que exige "Gerente").
  * **ERRO 500 (Server Error) ou `ProgrammingError`:**
      * *Mensagem:* `relação "authtoken_token" não existe`
      * *Causa:* Você esqueceu de rodar `python manage.py migrate` depois de adicionar `rest_framework.authtoken`.
