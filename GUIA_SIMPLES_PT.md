# 📱 GUIA SIMPLES - MacroDroid em Português

## ⚙️ PASSO 1: Criar a Macro

1. Abra o **MacroDroid**
2. Toque no **botão +** (azul, canto inferior direito)
3. Digite o nome: **Controle Financeiro**
4. Toque em **OK**

---

## 🔔 PASSO 2: Adicionar GATILHO (quando disparar)

1. Toque em **+ Gatilho** (ou **+ Trigger**)
2. Escolha: **Notificações**
3. Escolha: **Notificação Recebida**
4. Em **Aplicativos**, toque em **Selecionar Aplicativos**
5. Marque seus bancos:
   - ✅ Nubank
   - ✅ Inter
   - ✅ C6 Bank
   - ✅ Itaú
   - ✅ Outros bancos
6. Toque em **OK**

### ⚠️ IMPORTANTE: Configurar Filtros

Você verá 2 opções de filtro:

**Opção 1 - Filtro de Título:** (deixe vazio)

**Opção 2 - Filtro de Texto de Mensagem:**
- Digite apenas UMA palavra: `compra`
- OU use: `R$` (funciona para todas as notificações com valor)

**Tipo de Correspondência:**
- Escolha: **Contém** (ou **Contains**)

💡 **DICA**: Como o MacroDroid não deixa adicionar múltiplas palavras facilmente, use apenas `R$` no filtro. Isso vai capturar TODAS as notificações de compra que têm valor em reais!

7. Toque no **✓** (confirmar)

---

## ⚡ PASSO 3: Adicionar AÇÃO (o que fazer)

1. Toque em **+ Ação** (ou **+ Action**)
2. Escolha: **Conectividade**
3. Escolha: **Solicitação HTTP** (ou **HTTP Request**)

### Configure assim:

**URL:**
```
https://controle-financeiro-412p.onrender.com/webhook
```

**Método:**
- Escolha: **POST**

**Tipo de Conteúdo:** (pode aparecer como "Content Type" ou "Tipo MIME")
- Procure por um dropdown/menu
- Se encontrar, escolha: **application/json**
- ⚠️ **SE NÃO ACHAR**: Pule esta etapa, não é obrigatório!

**Cabeçalhos:** (toque em **+ Adicionar Cabeçalho** ou **+ Add Header**)

💡 **IMPORTANTE**: Adicione 2 cabeçalhos:

**Cabeçalho 1:**
- Nome: `Content-Type`
- Valor: `application/json`

**Cabeçalho 2:**
- Nome: `X-Token`
- Valor: `0a7a5d76-5012-4f38-8140-c16319253f20`

**Corpo:**

⚠️ **COPIE E COLE EXATAMENTE ISSO** (depois só troque o email):

```json
{"raw_text":"{notif_text}","app_name":"{notif_app}","user_email":"SEU_EMAIL_AQUI"}
```

👉 **Exemplo com email trocado:**
```json
{"raw_text":"{notif_text}","app_name":"{notif_app}","user_email":"joao@gmail.com"}
```

✅ **SIM, pode copiar e colar direto!**
⚠️ **NÃO MUDE** `{notif_text}` e `{notif_app}` - são variáveis do MacroDroid!
✏️ **SÓ TROQUE** `SEU_EMAIL_AQUI` pelo seu email de cadastro!

4. Toque no **✓** (confirmar)

---

## ✅ PASSO 4: Salvar

1. Toque no **✓** no canto superior direito
2. Verifique se o **toggle está VERDE** (ativado)

---

## 🧪 TESTAR

### Opção 1: Teste Rápido
1. Toque na macro criada
2. Toque em **Testar Ações**
3. Escolha um banco
4. Digite: `Compra aprovada de R$ 10,00 no TESTE`
5. Execute

### Opção 2: Teste Real
1. Faça uma compra pequena
2. Aguarde a notificação
3. Acesse: https://controle-financeiro-412p.onrender.com
4. Veja se apareceu!

---

## ❓ DÚVIDAS COMUNS

**Não acho "Conectividade":**
- Procure por "Connectivity" ou role até o final da lista

**Não acho "Solicitação HTTP":**
- Procure por "HTTP Request" ou "Web Request"

**Não acho "Cabeçalhos":**
- Procure por "Headers"
- Pode estar escondido, role para baixo

**Não acho "Corpo":**
- Procure por "Body" ou "Request Body"

---

## 📸 RESUMO VISUAL

```
MACRO: Controle Financeiro
├── 🔔 GATILHO
│   └── Notificação Recebida
│       ├── Apps: Nubank, Inter, etc
│       └── Filtro: compra, pagamento
│
└── ⚡ AÇÃO
    └── Solicitação HTTP
        ├── URL: https://controle-financeiro-412p.onrender.com/webhook
        ├── Método: POST
        ├── Tipo: application/json
        ├── Cabeçalho: X-Token = seu-token
        └── Corpo: JSON com notif_text e seu email
```

---

## 🆘 PRECISA DE AJUDA?

**Tire print da tela** onde está com dificuldade e me mostre!

Ou me diga:
1. Em qual passo você está?
2. O que aparece na sua tela?
3. Qual opção você não está encontrando?
