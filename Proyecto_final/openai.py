from dotenv import load_dotenv
from pandasai import SmartDataframe
import pandas as pd
from pandasai.llm import OpenAI
from sqlalchemy import create_engine, inspect
import warnings
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener credenciales desde las variables de entorno
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
api_token = os.getenv("API_TOKEN")

# Agregar nuestro API Key copiado desde la página de OpenAI
llm = OpenAI(api_token=api_token)

# Construir la cadena de conexión para SQLAlchemy
db_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

# Crear un objeto de motor SQLAlchemy
engine = create_engine(db_uri)

# Utilizar el inspector de SQLAlchemy para obtener la lista de tablas
inspector = inspect(engine)
tables = inspector.get_table_names()

# Mostrar al usuario la lista de tablas y solicitar que seleccione una
print("Lista de tablas disponibles:")
for i, table in enumerate(tables, 1):
    print(f"{i}. {table}")

# Solicitar al usuario que seleccione una tabla por su número
table_index = int(input("Ingrese el número de la tabla que desea consultar: "))
selected_table = tables[table_index - 1]

# Obtener información sobre la estructura de la tabla seleccionada
columns = inspector.get_columns(selected_table)

# Imprimir los nombres de los campos de la tabla
print(f"\nNombres de los campos de la tabla {selected_table}:")
for column in columns:
    print(column['name'])

# Consulta SQL para extraer datos de la tabla seleccionada por el usuario
query = f"SELECT * FROM {selected_table}"

# Utilizar pandas para leer la consulta directamente en un DataFrame
df = pd.read_sql_query(query, con=engine)

# Convertir el DataFrame en un DataFrame de Inteligencia Artificial
ai_df = SmartDataframe(df, config={"llm": llm})

# Imprimir una muestra de los primeros 3 registros del DataFrame
print("\nMuestra un registro de la tabla para entender su composición")
print(ai_df.head(1))

# Rutina para que el usuario realice consultas al DataFrame
while True:
    user_query = input("\nIngrese una consulta a la tabla (o 's' para salir): ")
    if user_query.lower() == 's':
        print("\n¡Hasta luego! Gracias por usar UrbanoIA")
        break
    try:
        # Ejemplo: Filtrar el DataFrame en función de la consulta del usuario
        result = ai_df.chat(user_query)
        print("\nResultado de la consulta:")
        print(result)
        print("\nÚltimo código generado por el modelo:")
        print(ai_df.last_code_generated)
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
