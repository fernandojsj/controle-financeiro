# Configuração MacroDroid - Controle Financeiro

## 📱 Configuração do Webhook no MacroDroid

### Passo 1: Obter suas credenciais

1. Acesse o Render Dashboard: https://dashboard.render.com
2. Vá em seu serviço `controle-financeiro`
3. Clique em "Environment"
4. Copie o valor de `WEBHOOK_TOKEN`

### Passo 2: Configurar Macro no MacroDroid

**TRIGGER (Gatilho):**
- Notification Received
- Selecione os apps dos bancos: Nubank, Inter, C6, etc.
- Filtro de texto: "compra" OU "pagamento" OU "aprovad"

**ACTION (Ação):**
- HTTP Request
- Method: `POST`
- URL: `https://controle-financeiro-412p.onrender.com/webhook`
- Content Type: `application/json`
- Headers:
  ```
  X-Token: SEU_WEBHOOK_TOKEN_AQUI
  ```
- Body:
  ```json
  {
    "raw_text": "{notif_text}",
    "app_name": "{notif_app}",
    "user_email": "seu@email.com"
  }
  ```

### Passo 3: Substituir valores

- `SEU_WEBHOOK_TOKEN_AQUI` → Token copiado do Render
- `seu@email.com` → Email que você usou para registrar na aplicação

### Exemplo de notificação que funciona:

```
Compra aprovada de R$ 45,90 no IFOOD
Pagamento de R$ 120,00 em POSTO SHELL
Transação de R$ 35,50 na PADARIA SAO JOSE
```

## 🔍 Testando o Webhook

### Teste manual com curl:

```bash
curl -X POST https://controle-financeiro-412p.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Token: SEU_TOKEN" \
  -d '{
    "raw_text": "Compra aprovada de R$ 45,90 no IFOOD",
    "app_name": "Nubank",
    "user_email": "seu@email.com"
  }'
```

### Resposta esperada:
```json
{"status": "ok"}
```

## 📋 Formatos de notificação suportados

O sistema reconhece automaticamente:
- `R$ 45,90 no IFOOD`
- `BRL 120.00 em POSTO SHELL`
- `R$ 35,50 na PADARIA`

## 🏷️ Categorização automática

- **Alimentação**: ifood, restaurante, padaria, mercado, burguer, pizza
- **Transporte**: uber, 99, posto, ipiranga, shell, estacionamento
- **Lazer/Assinaturas**: netflix, amazon, spotify, steam, playstation, xbox
- **Saúde**: farmacia, drogasil, hospital, medico
- **Outros**: Demais estabelecimentos

## ⚠️ Troubleshooting

**Erro 403 - Token inválido:**
- Verifique se o header `X-Token` está correto
- Confirme o token no Render Dashboard

**Erro 404 - Usuário não encontrado:**
- Verifique se o `user_email` está correto
- Confirme que você criou uma conta em `/registro`

**Gasto não aparece:**
- Verifique se a notificação contém "R$" ou "BRL"
- Confirme que o formato está correto
- Veja os logs no Render Dashboard
