import os
import json
from sqlalchemy import MetaData, Table, create_engine, insert, delete
import pandas as pd
from datetime import datetime, timedelta
from Google import create_service



SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = "1Ex9nb1GkDg6ibVsOlgDz8087HpLMVLOjTZLYJC00ktU"


def get_creds():
    CLIENT_SECRET_FILE = 'client_secret_apps.json'
    API_NAME = 'sheets'
    API_VERSION = 'v4'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION,SCOPES )
    return service

def get_sheet_trabajador(service, SHEET_ID, headers, values):
    print(SHEET_ID)
    RANGE = "Datos!A1"
    data = [headers] + values

    body = { 'values': data}

    try:
        sheet = service.spreadsheets()
        result = sheet.values().update(spreadsheetId=SHEET_ID,
                                    range=RANGE,
                                    valueInputOption='USER_ENTERED',
                                    body=body).execute()
        print(result)
    
    except Exception as e:
            raise(e)

def connect_bd():
    mssql_engine = create_engine(
        f"mssql+pyodbc://adminpowerbi:powerbi.2021@192.168.1.34,1433/SII?driver=ODBC+Driver+17+for+SQL+Server",
        pool_reset_on_return=None,
    )
    return mssql_engine

def leer_sql(conn):
    stmt = """SELECT [Razon_social]
      ,[Folio]
      ,[Periodo]
      ,[RUT]
	  ,*
        FROM [SII].[dbo].[declaracion_mensual_f29]
    """
    df = pd.read_sql(stmt, conn)
    return df

def quitar_columnas_duplicadas(df):
    df = df.loc[:,~df.columns.duplicated()]
    return df

def quitar_duplicados(df):
    df = df.drop_duplicates()
    return df

if __name__ == '__main__':
    conn = connect_bd()
    df = leer_sql(conn)
    df = quitar_columnas_duplicadas(df)
    df = df.drop_duplicates()
    print(df.columns)
    values = df.values.tolist()
    headers = df.columns.tolist()
    service = get_creds()
    get_sheet_trabajador(service, SHEET_ID, headers, values)
    print("Done")