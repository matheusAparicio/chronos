import calendar
from datetime import datetime


def normalizeMonth(dateStr: str) -> str:
    """
    Receives a month string in 'mm-yyyy' or 'yyyy-mm' format
    and always returns it in 'yyyy-mm' format.
    """
    dateParts = dateStr.split('-')
    
    if len(dateParts) != 2:
        raise ValueError("Formato inválido. Use 'mm-yyyy' ou 'yyyy-mm'.")
        
    # If the first part has 4 digits, it is already 'yyyy-mm'
    if len(dateParts[0]) == 4:
        return dateStr
    # If the second part has 4 digits, it is 'mm-yyyy', so we invert it
    elif len(dateParts[1]) == 4:
        return f"{dateParts[1]}-{dateParts[0]}"
    else:
        raise ValueError("Ano com 4 dígitos não encontrado.")

def normalizeDate(dateStr: str) -> str:
    """
    Receives a date string in 'dd-mm-yyyy' or 'yyyy-mm-dd' format
    and always returns it in 'yyyy-mm-dd' format.
    """
    dateParts = dateStr.split('-')
    
    if len(dateParts) != 3:
        raise ValueError("Formato inválido. Use 'dd-mm-yyyy' ou 'yyyy-mm-dd'.")
        
    # If the first part has 4 digits, it is already 'yyyy-mm-dd'
    if len(dateParts[0]) == 4:
        return dateStr
    # If the third part has 4 digits, it is 'dd-mm-yyyy', so we invert the order
    elif len(dateParts[2]) == 4:
        return f"{dateParts[2]}-{dateParts[1]}-{dateParts[0]}"
    else:
        raise ValueError("Ano com 4 dígitos não encontrado.")
    
def getFirstMonthDay(month):
    # Try to parse the input string to ensure correct format
    try:
        targetDate = datetime.strptime(month, "%Y-%m")
        
        # The first day of the month is always 1
        firstDay = targetDate.replace(day=1)
        
        # Return the formatted string yyyy-mm-dd
        return firstDay.strftime("%Y-%m-%d")
        
    except ValueError:
        print("Erro: A data informada é inválida. Por favor, use o formato 'yyyy-mm'.")
        return None
    
def getLastMonthDay(month):
    # Try to parse the input string to ensure correct format
    try:
        targetDate = datetime.strptime(month, "%Y-%m")
        
        targetYear = targetDate.year
        targetMonth = targetDate.month
        
        # calendar.monthrange returns a tuple: (weekday of first day, number of days in month)
        # We only need the second value (the total days)
        _, totalDaysInMonth = calendar.monthrange(targetYear, targetMonth)
        
        # Replace the day in our date object with the last day of the month
        lastDay = targetDate.replace(day=totalDaysInMonth)
        
        # Return the formatted string yyyy-mm-dd
        return lastDay.strftime("%Y-%m-%d")
        
    except ValueError:
        print("Erro: A data informada é inválida. Por favor, use o formato 'yyyy-mm'.")
        return None
    
def extractProperties(notionPagesList):
    # Check if the provided input is a valid list
    if not isinstance(notionPagesList, list):
        print("Erro: O formato fornecido não é uma lista válida.")
        return []

    # Create a new list containing only the 'properties' of each object
    # It also checks if the item is a dictionary and contains the 'properties' key
    propertiesList = [
        pageObj["properties"] 
        for pageObj in notionPagesList 
        if isinstance(pageObj, dict) and "properties" in pageObj
    ]

    # Optional: Alert if some objects didn't have the 'properties' key
    if len(propertiesList) < len(notionPagesList):
        print("Aviso: Alguns objetos na lista não continham a chave 'properties' e foram ignorados.")

    return propertiesList