from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel
import os
import json
from typing import Dict, Any

# =========================================================================
# 1. Definir o Modelo de Dados (Opcional, mas Altamente Recomendado)
#    Use a documentação da sua API para mapear a estrutura do JSON de Inscrição.
#    Isso permite que o FastAPI valide os dados de entrada automaticamente.
# =========================================================================

# Exemplo de um modelo de dados para a Inscrição (ajuste conforme a sua API)
class InscricaoPayload(BaseModel):
    id_inscricao: int
    nome_participante: str
    email: str
    status_inscricao: str
    data_evento: str

# Inicializa a aplicação FastAPI
app = FastAPI(title="Webhook de Inscrições")

# =========================================================================
# 2. O Endpoint do Webhook
#    O decorator (@app.post) define a rota e o método HTTP (POST)
# =========================================================================

# Rota do webhook (Use a rota que você deseja colocar no campo 'URL' da API)
@app.post("/webhook-inscricoes", status_code=status.HTTP_201_CREATED)
async def receber_webhook_inscricao(
    # Aqui, o FastAPI tenta mapear o JSON de entrada para o modelo (validação automática!)
    dados_inscricao: InscricaoPayload,
    # Você pode injetar a Requisição se precisar de headers (ex: para Autenticação)
    request: Request
):
    """
    Recebe o Webhook da plataforma de inscrições, processa os dados 
    e retorna o código 201 em até 5 segundos.
    """
    
    # ---------------------------------------------------------------------
    # Lógica de Autenticação (IMPORTANTE se a API exigir)
    # ---------------------------------------------------------------------
    # Exemplo: Se a API enviar um token no Header 'X-Auth-Token':
    # expected_token = os.environ.get("API_SECRET_TOKEN")
    # sent_token = request.headers.get("X-Auth-Token")
    #
    # if sent_token != expected_token:
    #     # Retornar 401 Unauthoized (Não Autorizado)
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, 
    #         detail="Token de Autenticação Inválido"
    #     )
        
    # ---------------------------------------------------------------------
    # Lógica de Processamento de Dados para o Hop
    # ---------------------------------------------------------------------
    
    # Converta o modelo Pydantic para um dicionário para manipulação/armazenamento
    dados_dict = dados_inscricao.model_dump()
    
    # Neste ponto, você SALVA os dados para que o Hop possa buscá-los.
    # Opções mais robustas em nuvem:
    # 1. Armazenar em um Banco de Dados (ex: PostgreSQL no Render).
    # 2. Enviar para uma Fila de Mensagens (ex: Redis/Kafka) que o Hop consome.

    print(f"Webhook Recebido para a inscrição ID: {dados_dict['id_inscricao']}")
    
    # Exemplo: Salvar em um arquivo local (NÃO PERSISTENTE NO RENDER PADRÃO, 
    # use apenas para teste local. Use um BD para produção!)
    # with open("inscricoes.jsonl", "a") as f:
    #    f.write(json.dumps(dados_dict) + "\n")


    # ---------------------------------------------------------------------
    # Resposta
    # ---------------------------------------------------------------------
    # O FastAPI já garante o status 201 (CREATED) pelo decorator.
    # O retorno pode ser uma mensagem de confirmação.
    return {"mensagem": "Inscrição recebida com sucesso. Processando para relatório."}

# =========================================================================
# 3. Configuração de Inicialização (para Gunicorn/Uvicorn)
# =========================================================================
# Você não precisa desse bloco se estiver usando Gunicorn/Uvicorn em produção.
# O Render usará o Start Command abaixo.