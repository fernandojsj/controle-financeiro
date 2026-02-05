# 📱 Guia Completo: MacroDroid + Controle Financeiro

## 🎯 Objetivo
Capturar notificações de bancos automaticamente e enviar para seu dashboard financeiro.

---

## 📋 Pré-requisitos

1. ✅ Conta criada em: https://controle-financeiro-412p.onrender.com/registro
2. ✅ MacroDroid instalado no celular
3. ✅ Token do webhook (veja abaixo como obter)

---

## 🔑 Passo 1: Criar e Configurar o Token do Webhook

### 1.1 - Gerar um Token Seguro

Escolha uma das opções:

**Opção A - Online (Rápido):**
1. Acesse: https://www.uuidgenerator.net/
2. Copie o UUID gerado (ex: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

**Opção B - PowerShell:**
```powershell
[guid]::NewGuid().ToString()
```

**Opção C - Criar manualmente:**
- Use uma senha forte aleatória (mínimo 32 caracteres)
- Exemplo: `meutoken123456789abcdefghijklmnop`

### 1.2 - Adicionar no Render

1. Acesse: https://dashboard.render.com
2. Faça login
3. Clique no serviço **controle-financeiro-412p**
4. Vá em **Environment** (menu lateral esquerdo)
5. Clique em **Add Environment Variable**
6. Preencha:
   - **Key**: `WEBHOOK_TOKEN`
   - **Value**: Cole o token que você gerou
7. Clique em **Save Changes**
8. ⚠️ **Aguarde ~2 minutos** - O Render vai reiniciar o serviço automaticamente
9. **Copie e guarde o token** - você vai usar no MacroDroid

---

## 📲 Passo 2: Criar Macro no MacroDroid (DETALHADO)

### 2.1 - Abrir MacroDroid e Criar Nova Macro

1. **Abra o app MacroDroid** no seu celular
2. Na tela inicial, você verá uma lista de macros (pode estar vazia)
3. **Toque no botão "+"** (botão azul flutuante no canto inferior direito)
4. Uma tela aparecerá pedindo o nome da macro
5. **Digite**: `Controle Financeiro`
6. **Toque em OK**
7. Você verá uma tela com 3 seções vazias:
   - 🔔 **TRIGGERS** (Gatilhos)
   - ⚡ **ACTIONS** (Ações)
   - ❓ **CONSTRAINTS** (Restrições - ignore esta)

---

### 2.2 - Configurar TRIGGER (Quando a macro vai disparar)

#### 2.2.1 - Adicionar Trigger de Notificação

1. **Toque em "+ TRIGGER"** (na seção de gatilhos)
2. Uma lista de categorias aparecerá
3. **Role para baixo** e toque em **"Notifications"**
4. Toque em **"Notification Received"**
5. Uma tela de configuração abrirá

#### 2.2.2 - Selecionar Apps dos Bancos

1. Na seção **"Applications"**, toque em **"Select Applications"**
2. Uma lista com TODOS os apps do celular aparecerá
3. **Role e marque** os apps dos seus bancos:
   - 📱 Nubank
   - 📱 Inter
   - 📱 C6 Bank
   - 📱 Itaú
   - 📱 Bradesco
   - 📱 Santander
   - 📱 PicPay
   - 📱 Qualquer outro banco que você usa
4. **Toque em OK** quando terminar

#### 2.2.3 - Configurar Filtro de Texto

1. Na mesma tela, procure por **"Text Filter"**
2. **Toque no campo de texto** abaixo de "Text Filter"
3. **Digite** (uma palavra por vez, apertando Enter após cada):
   ```
   compra
   ```
   Aperte **Enter**, depois digite:
   ```
   pagamento
   ```
   Aperte **Enter**, depois digite:
   ```
   aprovad
   ```
   Aperte **Enter**, depois digite:
   ```
   transação
   ```
   Aperte **Enter**, depois digite:
   ```
   débito
   ```

4. **IMPORTANTE**: Procure por **"Match Type"** e selecione **"Match Any"**
   - Isso significa: "disparar se a notificação contiver QUALQUER uma dessas palavras"

5. **Toque no ✓** (check) no canto superior direito para confirmar

6. Você voltará para a tela da macro e verá o trigger adicionado

---

### 2.3 - Configurar ACTION (O que a macro vai fazer)

#### 2.3.1 - Adicionar Ação HTTP Request

1. **Toque em "+ ACTION"** (na seção de ações)
2. Uma lista de categorias aparecerá
3. **Toque em "Connectivity"**
4. **Toque em "HTTP Request"**
5. Uma tela de configuração detalhada abrirá

#### 2.3.2 - Configurar URL

1. No campo **"URL"**, **apague** o que estiver lá
2. **Digite ou cole**:
   ```
   https://controle-financeiro-412p.onrender.com/webhook
   ```
3. ⚠️ **ATENÇÃO**: Não deixe espaços no início ou fim!

#### 2.3.3 - Configurar Method

1. Procure por **"Method"**
2. **Toque** no dropdown (pode estar como GET)
3. **Selecione**: **POST**

#### 2.3.4 - Configurar Content Type

1. Procure por **"Content Type"**
2. **Toque** no dropdown
3. **Selecione**: **application/json**

#### 2.3.5 - Adicionar Header (TOKEN DE SEGURANÇA)

1. **Role para baixo** até encontrar **"Headers"**
2. **Toque em "+ Add Header"** ou "Add" (botão pequeno ao lado)
3. Dois campos aparecerão:

   **Campo 1 - Header Name:**
   ```
   X-Token
   ```
   
   **Campo 2 - Header Value:**
   ```
   0a7a5d76-5012-4f38-8140-c16319253f20
   ```
   ⚠️ **IMPORTANTE**: Use o token que você configurou no Render!

4. **Toque em OK** ou confirme

#### 2.3.6 - Configurar Body (DADOS A ENVIAR)

1. **Role para baixo** até encontrar **"Body"**
2. **Toque no campo de texto** grande
3. **Apague** tudo que estiver lá
4. **Cole ou digite EXATAMENTE** (respeitando as aspas e chaves):

```json
{
  "raw_text": "{notif_text}",
  "app_name": "{notif_app}",
  "user_email": "seu@email.com"
}
```

5. ⚠️ **SUBSTITUA** `seu@email.com` pelo email que você usou para criar conta no site!
   - Exemplo: se seu email é `joao@gmail.com`, ficará:
   ```json
   {
     "raw_text": "{notif_text}",
     "app_name": "{notif_app}",
     "user_email": "joao@gmail.com"
   }
   ```

6. **NÃO MUDE** `{notif_text}` e `{notif_app}` - são variáveis do MacroDroid!

7. **Toque no ✓** (check) no canto superior direito para confirmar

---

### 2.4 - Salvar e Ativar a Macro

1. Você voltará para a tela da macro
2. Agora você verá:
   - ✅ 1 TRIGGER configurado (Notification Received)
   - ✅ 1 ACTION configurada (HTTP Request)
3. **Toque no ✓** (check) no canto superior direito
4. A macro será salva
5. **VERIFIQUE**: O toggle ao lado da macro deve estar **VERDE** (ativado)
   - Se estiver cinza, toque nele para ativar

---

### 2.5 - Dar Permissões (SE NECESSÁRIO)

O MacroDroid pode pedir permissões:

1. **Acesso a Notificações**: Toque em "Grant" e ative nas configurações
2. **Acesso à Internet**: Geralmente já está permitido
3. **Executar em segundo plano**: Permita para funcionar sempre

---

## 🧪 Passo 3: Testar

### Teste 1: Notificação Real
1. Faça uma compra pequena com seu cartão
2. Aguarde a notificação do banco
3. Acesse: https://controle-financeiro-412p.onrender.com
4. Verifique se o gasto apareceu!

### Teste 2: Notificação Manual (Simulação)
1. No MacroDroid, toque na macro criada
2. Toque em **Test Actions**
3. Selecione um app de banco
4. Digite uma notificação de teste:
   ```
   Compra aprovada de R$ 10,00 no TESTE MACRODROID
   ```
5. Execute
6. Verifique no dashboard se apareceu

---

## 📝 Exemplos de Notificações que Funcionam

✅ **Nubank:**
```
Compra aprovada
R$ 45,90 no IFOOD
```

✅ **Inter:**
```
Pagamento de R$ 120,00 em POSTO SHELL
```

✅ **C6:**
```
Transação aprovada: R$ 35,50 - PADARIA SAO JOSE
```

✅ **Itaú:**
```
Compra no débito de R$ 89,90 em MERCADO EXTRA
```

---

## 🔧 Troubleshooting

### ❌ Gasto não aparece no dashboard

**Problema 1: Token inválido**
- Verifique se copiou o token correto do Render
- Confirme que não tem espaços extras no header

**Problema 2: Email incorreto**
- Verifique se o email no body é o mesmo usado no registro
- Teste fazer login com esse email

**Problema 3: Formato da notificação**
- Verifique se a notificação contém "R$" ou "BRL"
- Confirme que tem o nome do estabelecimento

**Problema 4: Macro não dispara**
- Verifique se o app do banco está selecionado no trigger
- Confirme que os filtros de texto estão corretos
- Teste com "Match Any" ativado

### 🔍 Ver Logs de Erro

1. Acesse: https://dashboard.render.com
2. Clique no serviço **controle-financeiro**
3. Vá em **Logs**
4. Procure por erros recentes

---

## 💡 Dicas

1. **Privacidade**: O MacroDroid só envia notificações dos apps selecionados
2. **Bateria**: O impacto é mínimo, apenas quando recebe notificação
3. **Offline**: Se estiver sem internet, a notificação é perdida (não há fila)
4. **Múltiplos dispositivos**: Configure em cada celular que você usa

---

## 🎨 Categorização Automática

O sistema categoriza automaticamente baseado no estabelecimento:

- 🍔 **Alimentação**: ifood, restaurante, padaria, mercado, burguer, pizza
- 🚗 **Transporte**: uber, 99, posto, ipiranga, shell, estacionamento
- 🎮 **Lazer**: netflix, amazon, spotify, steam, playstation, xbox
- 💊 **Saúde**: farmacia, drogasil, hospital, medico
- 📦 **Outros**: Demais estabelecimentos

---

## 📞 Suporte

Problemas? Verifique:
1. Token está correto
2. Email está correto
3. Macro está ativa (toggle verde)
4. App do banco está nas permissões de notificação

---

**Pronto! Agora seus gastos são registrados automaticamente! 🚀**
