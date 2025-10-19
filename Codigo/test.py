import psycopg2
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

# Obtener las variables
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

print("Intentando conectar a:", HOST)

# Conectarse a la base de datos
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        sslmode="require"  # Supabase requiere SSL
    )
    print("✅ Conexión exitosa a Supabase!")

    # Probar consulta simple
    cursor = connection.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("🕒 Fecha/hora actual en servidor:", result)

    cursor.close()
    connection.close()
    print("🔒 Conexión cerrada correctamente.")

except Exception as e:
    print(f"❌ Error al conectar: {e}")
