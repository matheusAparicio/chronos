import requests
import json
import os
from dotenv import load_dotenv


load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")


headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28" # Versão atual recomendada da API
}

def getNotionData():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    payload = {
        # "page_size": 2,
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        print(f"Encontrados {len(results)} registros de ponto.")
        
        # Exemplo básico de parsing:
        for page in results:
            # A estrutura exata do 'properties' vai depender de como você nomeou as colunas
            # Aqui é um exemplo genérico acessando o nome/título da página e propriedades
            properties = page.get("properties", {})

            print(json.dumps(properties, indent=2))
            
        return results
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    registers = getNotionData()
