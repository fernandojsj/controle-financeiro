#!/usr/bin/env python3

import asyncio
from app.main import app
from app.database import get_session
from app.main import WebhookPayload, receber_gasto

async def test_webhook():
    try:
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        print("Testando múltiplas mensagens...\n")
        
        # Teste diferentes mensagens do Nubank
        test_messages = [
            "Compra aprovada R$ 15,90 no MERCADO LIVRE",
            "Compra aprovada R$ 45,00 no UBER",
            "Compra aprovada R$ 120,50 no POSTO SHELL",
            "Compra aprovada R$ 8,50 no PADARIA SAO BENTO"
        ]
        
        for msg in test_messages:
            payload = WebhookPayload(
                raw_text=msg,
                app_name="Nubank"
            )
            result = await receber_gasto(payload, session)
            print(f"Mensagem: {msg}")
            print(f"Resultado: {result}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_webhook())