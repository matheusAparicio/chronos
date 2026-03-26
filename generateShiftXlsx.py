import requests
from pathlib import Path
import os
import sys
import openpyxl
from utilities import *
from dotenv import load_dotenv
from constants import *
from datetime import datetime, timedelta


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
        "page_size": REGISTERS_FETCH_LIMIT,
        "filter": {},
    }

    if (month):
        payload["filter"]["and"] = [
            {
                "property": NOTION_LABELS["created_at"], # <-- Altere para o nome exato da sua coluna
                "date": {
                    "on_or_after": getFirstMonthDay(month)
                }
            },
            {
                "property": NOTION_LABELS["created_at"],
                "date": {
                    "on_or_before": getLastMonthDay(month)
                }
            }
        ]
    elif (initialDate and finalDate):
        payload["filter"]["and"] = [
            {
                "property": NOTION_LABELS["created_at"], # <-- Altere para o nome exato da sua coluna
                "date": {
                    "on_or_after": initialDate
                }
            },
            {
                "property": NOTION_LABELS["created_at"],
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
        results = extractProperties(data.get("results", []))

        return results
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)

def parseNotionTime(timeStr):
    """
    Helper function to convert Notion ISO string to datetime 
    and apply UTC-3 timezone (Brazil).
    """
    if not timeStr:
        return None
    try:
        # Parse the string format: 2026-02-24T16:14:00.000Z
        dt = datetime.strptime(timeStr, "%Y-%m-%dT%H:%M:%S.%fZ")
        # Subtract 3 hours to match Brazilian timezone
        localDt = dt - timedelta(hours=3) 
        return localDt
    except ValueError:
        return None

def generateXlsx(registers):
    baseDir = Path(__file__).resolve().parent
    outputsDir = baseDir / "outputs"
    outputsDir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileName = f"{os.getenv("NAME")} - {os.getenv("TITLE")} - {month if month else f"{initialDate} -> {finalDate}"}.xlsx"
    finalPath = outputsDir / fileName
    
    templatePath = baseDir / "spreadsheet_template.xlsx"
    
    try:
        wb = openpyxl.load_workbook(templatePath)
        sheet = wb.active
        
        # --- 2. DATA PREPARATION (PAIRING) ---
        # Sort registers chronologically to ensure Entradas and Saídas match correctly
        sortedRegisters = sorted(
            registers, 
            key=lambda r: r.get(NOTION_LABELS["period"], {}).get("created_time", "")
        )
        
        shifts = []
        currentEntry = None
        
        # Group pairs of "Entrada" and "Saída"
        for reg in sortedRegisters:
            statusObj = reg.get(NOTION_LABELS["status"], {}).get("select")
            statusName = statusObj.get("name") if statusObj else ""
            
            if statusName == "Entrada":
                currentEntry = reg
            elif statusName == "Saída" and currentEntry:
                # --- EXTRACT DATA BEFORE APPENDING ---
                
                # 1. Extract Project
                projectObj = currentEntry.get(NOTION_LABELS["project"], {}).get("select")
                projectName = projectObj.get("name") if projectObj else "Evolução e Otimização de Sistemas"

                # 2. Extract Task
                taskArr = currentEntry.get(NOTION_LABELS["task"], {}).get("rich_text", [])
                if taskArr and len(taskArr) > 0:
                    taskName = "".join([textPart.get("plain_text", "") for textPart in taskArr])
                else:
                    taskName = "Apontamento de Horas"
                
                # 3. Extract Timestamps
                entryTimeStr = currentEntry.get(NOTION_LABELS["period"], {}).get("created_time", "")
                exitTimeStr = reg.get(NOTION_LABELS["period"], {}).get("created_time", "")
                
                entryDt = parseNotionTime(entryTimeStr)
                exitDt = parseNotionTime(exitTimeStr)
                
                # 4. Format Dates and Times
                # Using %H:%M to keep hours and minutes (e.g., 16:14)
                dateVal = entryDt.strftime("%d/%m/%Y") if entryDt else ""
                startTimeVal = entryDt.strftime("%H:%M:%S") if entryDt else ""
                endTimeVal = exitDt.strftime("%H:%M:%S") if exitDt else ""
                
                # Append clean, formatted data to shifts
                shifts.append({
                    "project": projectName,
                    "task": taskName,
                    "date": dateVal,
                    "startTime": startTimeVal,
                    "endTime": endTimeVal
                })
                
                # Clear current entry to find the next pair
                currentEntry = None
        
        # --- 3. WRITING TO EXCEL ---
        for index, shift in enumerate(shifts):
            rowIndex = index + 2
            
            # Stop if we exceed the allowed unprotected rows (limit is 41)
            if rowIndex > 41:
                break
            
            # Populate cells using the clean dictionary and constants
            sheet.cell(row=rowIndex, column=SPREADSHEET_COLUMNS["name"], value=os.getenv("NAME", "Teteu"))
            sheet.cell(row=rowIndex, column=SPREADSHEET_COLUMNS["project"], value=shift["project"])
            sheet.cell(row=rowIndex, column=SPREADSHEET_COLUMNS["task"], value=shift["task"])
            sheet.cell(row=rowIndex, column=SPREADSHEET_COLUMNS["date"], value=shift["date"])
            sheet.cell(row=rowIndex, column=SPREADSHEET_COLUMNS["initial_timestamp"], value=shift["startTime"])
            sheet.cell(row=rowIndex, column=SPREADSHEET_COLUMNS["final_timestamp"], value=shift["endTime"])
        
        wb.save(finalPath)
        print(f"Sucesso! Arquivo gerado em: {finalPath}")
        return str(finalPath)
        
    except Exception as e:
        print(f"Erro ao gerar o arquivo Excel: {e}")
        return None

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
    print(f"Encontrados {len(registers)} registros de ponto.")

    generateXlsx(registers)
