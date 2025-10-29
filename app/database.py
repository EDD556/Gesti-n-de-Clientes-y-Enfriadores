import reflex as rx
from supabase import create_client, Client
import os
import logging

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jyzbjmnklwftdkdupkbh.supabase.co")
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5emJqbW5rbHdmdGRrZHVwa2JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2NjM2MzgsImV4cCI6MjA3NzIzOTYzOH0.5KqcDDUgejnPVBSJeWR48hDB26jTbU-z4YmP9cPlPYE",
)


def get_db_client() -> Client | None:
    """Creates and returns a Supabase client, or None if connection fails."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logging.error("Supabase URL or Key is not configured.")
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logging.exception(f"Failed to create Supabase client: {e}")
        return None


def get_init_db_sql() -> str:
    """Returns the SQL script to initialize the database in Supabase."""
    return """
    CREATE TABLE IF NOT EXISTS clientes (
        numero_cliente TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        frecuencia_entrega TEXT,
        frecuencia_preventa TEXT
    );

    CREATE TABLE IF NOT EXISTS enfriadores (
        serie TEXT PRIMARY KEY,
        canal TEXT,
        modelo TEXT
    );

    CREATE TABLE IF NOT EXISTS tipos_tramite (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS documentos_tramite (
        id SERIAL PRIMARY KEY,
        tipo_tramite_id INTEGER NOT NULL,
        nombre_documento TEXT NOT NULL,
        FOREIGN KEY (tipo_tramite_id) REFERENCES tipos_tramite(id)
    );

    CREATE TABLE IF NOT EXISTS documentos_enfriadores (
        id SERIAL PRIMARY KEY,
        nombre_documento TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS tramites (
        id SERIAL PRIMARY KEY,
        tipo_tramite_id INTEGER NOT NULL,
        cliente_numero TEXT NOT NULL,
        numero_contacto TEXT,
        fecha DATE,
        comentarios TEXT,
        estatus TEXT NOT NULL,
        FOREIGN KEY (tipo_tramite_id) REFERENCES tipos_tramite(id) ON DELETE CASCADE,
        FOREIGN KEY (cliente_numero) REFERENCES clientes(numero_cliente) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tramites_documentos (
        tramite_id INTEGER NOT NULL,
        documento_tramite_id INTEGER NOT NULL,
        PRIMARY KEY (tramite_id, documento_tramite_id),
        FOREIGN KEY (tramite_id) REFERENCES tramites(id) ON DELETE CASCADE,
        FOREIGN KEY (documento_tramite_id) REFERENCES documentos_tramite(id) ON DELETE CASCADE
    );

    -- Function for advanced search
    CREATE OR REPLACE FUNCTION get_tramites_filtrados(p_estatus TEXT DEFAULT NULL)
    RETURNS TABLE (
        id INT,
        tipo_tramite_nombre TEXT,
        cliente_nombre TEXT,
        numero_contacto TEXT,
        fecha TEXT,
        estatus TEXT
    )
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            t.id,
            COALESCE(tt.nombre, 'Tipo Desconocido') as tipo_tramite_nombre,
            COALESCE(c.nombre, 'Cliente Desconocido') as cliente_nombre,
            t.numero_contacto,
            t.fecha::TEXT,
            t.estatus
        FROM tramites t
        LEFT JOIN tipos_tramite tt ON t.tipo_tramite_id = tt.id
        LEFT JOIN clientes c ON t.cliente_numero = c.numero_cliente
        WHERE p_estatus IS NULL OR t.estatus = p_estatus
        ORDER BY t.id DESC;
    END; 
    $$ LANGUAGE plpgsql;
    """


def init_db():
    """Provides instructions to initialize the Supabase database."""
    sql_script = get_init_db_sql()
    logging.info("""

===== INSTRUCCIONES PARA INICIALIZAR LA BASE DE DATOS SUPABASE ======""")
    logging.info(
        "1. Inicia sesión en tu panel de Supabase: https://supabase.com/dashboard"
    )
    logging.info("2. Navega a la sección 'SQL Editor'.")
    logging.info("3. Haz clic en '+ New query'.")
    logging.info("4. Copia y pega el siguiente script SQL en el editor:")
    logging.info(
        """
"""
        + sql_script
    )
    logging.info(
        "5. Haz clic en 'RUN' para ejecutar el script y crear las tablas y funciones."
    )
    logging.info("""=========================================================================
""")