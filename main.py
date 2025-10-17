from fastapi import FastAPI, Request, status
from pydantic import BaseModel
import json
from datetime import datetime
from typing import List, Optional

# =========================================================================
# 1. Modelo de Dados (Baseado no JSON de Localização)
#    Esta validação é feita automaticamente pelo FastAPI/Pydantic.
# =========================================================================

class LocalizacaoEmTempoReal(BaseModel):
    vehicle_id: Optional[str] = None
    vin: Optional[str] = None # Vehicle Identification Number (Chassi)
    vehicle_identification: Optional[str] = None
    hour_meter: Optional[float] = None
    fuel_level: Optional[float] = None
    compass_bearing: int
    speed: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ts: Optional[datetime] = None # Timestamp da leitura (o Pydantic converte a string ISO para datetime)
    org_id: Optional[str] = None
    org_name: Optional[str] = None
    fields: Optional[List[str]] = None # Lista de strings, pode ser nulo/vazio

# =========================================================================
# 2. Configuração e Inicialização
# =========================================================================

app = FastAPI(title="Webhook de Localização (Somente Log)")

# =========================================================================
# 3. Endpoint do Webhook
# =========================================================================

# Rota configurada para /webhook-realtime (Conforme sugerido na correção do 404)
@app.post("/webhook-realtime", status_code=status.HTTP_201_CREATED)
async def receber_webhook_localizacao(
    # FastAPI/Pydantic tenta validar o JSON de entrada aqui:
    dados_localizacao: LocalizacaoEmTempoReal,
    request: Request
):
    """
    Recebe o Webhook POST, valida os dados, loga o conteúdo e retorna 201.
    A lógica de salvamento no DB foi REMOVIDA para fins de debug.
    """
    
    #dados_dict = dados_localizacao.model_dump()
    dados_json_string = dados_localizacao.model_dump_json(indent=4)
    # ---------------------------------------------------------------------
    # Lógica de Log (Visualização no Log do Render)
    # ---------------------------------------------------------------------
    
    # Geramos um log de confirmação e um log detalhado do dado:
    print("-" * 50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Webhook Recebido com Sucesso!")
    print(f"-> Veículo (VIN): {dados_dict['vin']}")
    print(f"-> Localização: {dados_dict['latitude']}, {dados_dict['longitude']}")
    print(f"-> Velocidade: {dados_dict['speed']} km/h")
    # Loga o JSON completo para garantir que todos os dados foram recebidos corretamente:
    print("-> Dados Completos (JSON):")
    #print(json.dumps(dados_dict, indent=4))
    print(dados_json_string)
    print("-" * 50)
    
    # ---------------------------------------------------------------------
    # Resposta (dentro do limite de 5 segundos)
    # ---------------------------------------------------------------------
    # Se o código chegar até aqui, significa que:
    # 1. A rota foi encontrada.
    # 2. O JSON foi validado pelo Pydantic.
    # 3. O status 201 será retornado.
    
    return {"status": "sucesso", "veiculo_recebido": dados_localizacao.vin, "mensagem": "Dados logados com sucesso."}

# Fim do main.py

