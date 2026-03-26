import requests
import json
import os
import sys
from utilities import *
from dotenv import load_dotenv
from constants import notionLabels


# Initial Definitions -----
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

month = None
initialDate = None
finalDate = None
# -------------------------

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28" # Versão atual recomendada da API
}

def getNotionData(month=None, initialDate=None, finalDate=None):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    payload = {
        # "page_size": 2,
        "filter": {},
    }

    if (month):
        payload["filter"]["and"] = [
            {
                "property": notionLabels["created_at"], # <-- Altere para o nome exato da sua coluna
                "date": {
                    "on_or_after": getFirstMonthDay(month)
                }
            },
            {
                "property": notionLabels["created_at"],
                "date": {
                    "on_or_before": getLastMonthDay(month)
                }
            }
        ]
    elif (initialDate and finalDate):
        payload["filter"]["and"] = [
            {
                "property": notionLabels["created_at"], # <-- Altere para o nome exato da sua coluna
                "date": {
                    "on_or_after": initialDate
                }
            },
            {
                "property": notionLabels["created_at"],
                "date": {
                    "on_or_before": finalDate
                }
            }
        ]
    else:
        raise Exception("Nenhuma data foi informada.")
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        # Exemplo básico de parsing:
        for page in results:
            # A estrutura exata do 'properties' vai depender de como você nomeou as colunas
            # Aqui é um exemplo genérico acessando o nome/título da página e propriedades
            properties = page.get("properties", {})

            print(json.dumps(properties, indent=2))

        print(f"Encontrados {len(results)} registros de ponto.")
            
        return results
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # If just one parameter, then it's the month.
    # If two parameters, then it's the initial and final date.
    argsLen = len(sys.argv)
    if (argsLen < 4):
        try:
            match(len(sys.argv)):
                case 1:
                    print("Nenhuma data foi informada.")
                    sys.exit()
                case 2:
                    month = normalizeMonth(sys.argv[1])
                case 3:
                    initialDate = normalizeDate(sys.argv[1])
                    finalDate = normalizeDate(sys.argv[2])
        except Exception as error:
            print(error)
            sys.exit()
    else:
        print("Informe apenas o mês ou data inicial e data final.")
        sys.exit()

    registers = getNotionData(month, initialDate, finalDate)
