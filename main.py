from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel
import os
import psycopg2 
from datetime import datetime
from typing import List, Optional # Usaremos List para "fields" e Optional para possíveis nulos

# =========================================================================
# 1. Modelo de Dados (AJUSTADO PARA LOCALIZAÇÃO DE VEÍCULOS)
# =========================================================================

class LocalizacaoEmTempoReal(BaseModel):
    vehicle_id: str
    vin: str # Vehicle Identification Number (Chassi)
    vehicle_identification: str
    hour_meter: float
    fuel_level: float
    compass_bearing: int
    speed: float
    latitude: float
    longitude: float
    ts: datetime # Timestamp da leitura (o Pydantic converte a string ISO para datetime)
    org_id: str
    org_name: str
    fields: Optional[List[str]] = None # Lista de strings, pode ser nulo/vazio

# =========================================================================
# 2. Configuração e Inicialização
# =========================================================================

app = FastAPI(title="Webhook de Localização em Tempo Real")
DB_URL = os.environ.get("DATABASE_URL")

# =========================================================================
# 3. Endpoint do Webhook
# =========================================================================

@app.post("/webhook-inscricoes", status_code=status.HTTP_201_CREATED)
async def receber_webhook_localizacao(
    dados_localizacao: LocalizacaoEmTempoReal,
    request: Request
):
    """
    Recebe o Webhook POST com dados de localização, salva no PostgreSQL e retorna 201.
    """
    
    # ... [ Lógica de Autenticação Opcional, mas RECOMENDADA! ] ...
    
    dados_dict = dados_localizacao.model_dump()
    
    conn = None
    cursor = None
    try:
        # 1. Conexão
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # 2. Query de Inserção (Ajuste os nomes das colunas conforme seu DB)
        # Note que separamos 'fields' para salvar a lista como JSONB no PostgreSQL 
        # (se a tabela suportar) ou convertemos para string.
        
        # Para simplificar, vamos juntar a lista 'fields' em uma única string:
        fields_str = ", ".join(dados_dict['fields']) if dados_dict['fields'] else None

        insert_query = """
        INSERT INTO localizacao_raw (
            vehicle_id, vin, vehicle_identification, hour_meter, fuel_level, 
            compass_bearing, speed, latitude, longitude, ts_leitura, 
            org_id, org_name, fields_tags, data_recebimento
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vehicle_id, ts_leitura) DO NOTHING;
        """
        
        # 3. Execução
        cursor.execute(insert_query, (
            dados_dict['vehicle_id'], dados_dict['vin'], dados_dict['vehicle_identification'], 
            dados_dict['hour_meter'], dados_dict['fuel_level'], dados_dict['compass_bearing'], 
            dados_dict['speed'], dados_dict['latitude'], dados_dict['longitude'], 
            dados_dict['ts'], dados_dict['org_id'], dados_dict['org_name'], 
            fields_str, datetime.now()
        ))
        
        conn.commit()
        
        print(f"Log: Localização do veículo {dados_dict['vin']} salva. Lat/Lon: {dados_dict['latitude']}/{dados_dict['longitude']}")
        
    except psycopg2.Error as e:
        if conn: conn.rollback()
        print(f"ERRO CRÍTICO NO DB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao persistir dados de localização."
        )
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return {"status": "sucesso", "veiculo_recebido": dados_localizacao.vin}



