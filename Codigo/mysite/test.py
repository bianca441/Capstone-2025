import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path

# === CARGAR VARIABLES DEL .env ===
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

print(f"📦 Cargando variables desde: {env_path}")
load_dotenv(env_path)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

print("\n📡 Intentando conectar a Supabase PostgreSQL...")
print(f"Host: {DB_HOST}")
print(f"Puerto: {DB_PORT}")
print(f"Usuario: {DB_USER}")
print(f"Base de datos: {DB_NAME}\n")

try:
    # Crear conexión
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        connect_timeout=10
    )

    print("✅ Conexión exitosa con Supabase.")
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print(f"🧠 Versión de PostgreSQL: {record[0]}")

    cursor.close()
    connection.close()
    print("🔒 Conexión cerrada correctamente.")

except Exception as e:
    print(f"❌ Error al conectar: {e}")
