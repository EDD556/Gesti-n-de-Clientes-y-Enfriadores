import reflex as rx
from typing import TypedDict, Optional
import pandas as pd
from app.database import get_db_client, init_db, get_init_db_sql
import logging
import json


class NavItem(TypedDict):
    name: str
    icon: str
    route: str


class TipoTramite(TypedDict):
    id: int
    nombre: str


class Documento(TypedDict):
    id: int
    nombre_documento: str


class Cliente(TypedDict):
    numero_cliente: str
    nombre: str
    frecuencia_entrega: str
    frecuencia_preventa: str


class Tramite(TypedDict):
    id: int
    tipo_tramite_nombre: str
    cliente_nombre: str
    numero_contacto: str
    fecha: str
    estatus: str


class State(rx.State):
    """The base state for the app."""

    current_page: str = "Configuración"
    nav_items: list[NavItem] = [
        {"name": "Configuración", "icon": "settings", "route": "/"},
        {"name": "Enfriadores", "icon": "box", "route": "/enfriadores"},
        {"name": "Trámites", "icon": "file-text", "route": "/tramites"},
    ]
    active_config_tab: str = "clientes"
    db_initialized: bool = False
    db_error_message: str = ""
    tipos_tramite: list[TipoTramite] = []
    selected_tipo_tramite_id: str = ""
    documentos_tramite: list[Documento] = []
    documentos_enfriadores: list[Documento] = []
    new_tramite_tipo_id: str = ""
    new_tramite_cliente_numero: str = ""
    new_tramite_cliente_data: Optional[Cliente] = None
    new_tramite_contacto: str = ""
    new_tramite_fecha: str = ""
    new_tramite_comentarios: str = ""
    new_tramite_estatus: str = "RECIBIDO"
    new_tramite_documentos_seleccionados: dict[str, bool] = {}
    estatus_options: list[str] = [
        "RECIBIDO",
        "RECHAZADO",
        "EN PROCESO",
        "PENDIENTE DE ENTREGA",
        "ENTREGADO",
    ]
    tramites: list[Tramite] = []
    filtro_estatus: str = ""

    @rx.event
    def initialize_app(self):
        """Initialize the app by loading initial data."""
        return State.load_initial_data

    @rx.event
    def load_initial_data(self):
        """Load initial data needed for the UI."""
        return [State.load_tipos_tramite, State.load_tramites]

    @rx.event
    def set_active_config_tab(self, tab: str):
        self.active_config_tab = tab
        if tab == "tramites":
            return State.load_tipos_tramite
        if tab == "docs_enfriadores":
            return State.load_documentos_enfriadores

    @rx.event
    async def handle_clientes_upload(self, files: list[rx.UploadFile]):
        if not files:
            return rx.toast.error("No se seleccionó ningún archivo.")
        file = files[0]
        try:
            upload_data = await file.read()
            df = pd.read_excel(upload_data, engine="openpyxl")
            df = df[
                [
                    "numero_cliente",
                    "nombre",
                    "frecuencia_entrega",
                    "frecuencia_preventa",
                ]
            ]
            df["numero_cliente"] = df["numero_cliente"].astype(str)
            df["frecuencia_entrega"] = df["frecuencia_entrega"].astype(str)
            df["frecuencia_preventa"] = df["frecuencia_preventa"].astype(str)
            client = get_db_client()
            if not client:
                return rx.toast.error("No se pudo conectar a la base de datos.")
            records = df.to_dict(orient="records")
            client.table("clientes").upsert(
                records, on_conflict="numero_cliente"
            ).execute()
            return rx.toast.success(f"{len(df)} registros de clientes importados.")
        except Exception as e:
            logging.exception(f"Error al procesar archivo de clientes: {e}")
            return rx.toast.error(f"Error al procesar el archivo: {e}")

    @rx.event
    async def handle_enfriadores_upload(self, files: list[rx.UploadFile]):
        if not files:
            return rx.toast.error("No se seleccionó ningún archivo.")
        file = files[0]
        try:
            upload_data = await file.read()
            df = pd.read_excel(upload_data, engine="openpyxl")
            df = df[["canal", "serie", "modelo"]]
            df["serie"] = df["serie"].astype(str)
            client = get_db_client()
            if not client:
                return rx.toast.error("No se pudo conectar a la base de datos.")
            records = df.to_dict(orient="records")
            client.table("enfriadores").upsert(records, on_conflict="serie").execute()
            return rx.toast.success(f"{len(df)} registros de enfriadores importados.")
        except Exception as e:
            logging.exception(f"Error al procesar archivo de enfriadores: {e}")
            return rx.toast.error(f"Error al procesar el archivo: {e}")

    @rx.event
    def add_tipo_tramite(self, form_data: dict):
        new_tipo_tramite_name = form_data.get("new_tipo_tramite_name", "").strip()
        if not new_tipo_tramite_name:
            return rx.toast.error("El nombre del tipo de trámite no puede estar vacío.")
        try:
            client = get_db_client()
            client.table("tipos_tramite").insert(
                {"nombre": new_tipo_tramite_name}
            ).execute()
            yield rx.toast.success("Tipo de trámite añadido.")
            yield State.load_tipos_tramite
        except Exception as e:
            logging.exception(f"Error al añadir tipo de trámite: {e}")
            return rx.toast.error("Error al añadir tipo de trámite. ¿Ya existe?")

    @rx.event(background=True)
    async def load_tipos_tramite(self):
        try:
            client = get_db_client()
            if not client:
                async with self:
                    self.db_initialized = False
                    self.db_error_message = (
                        "No se pudieron cargar las credenciales de Supabase."
                    )
                return
            response = (
                client.table("tipos_tramite")
                .select("id, nombre")
                .order("nombre")
                .execute()
            )
            async with self:
                self.tipos_tramite = response.data
                self.db_initialized = True
                self.db_error_message = ""
        except Exception as e:
            logging.exception(f"Error al cargar tipos de trámite: {e}")
            async with self:
                self.tipos_tramite = []
                self.db_initialized = False
                self.db_error_message = str(e)
            return rx.toast.error("Error de red al cargar tipos de trámite.")

    @rx.event
    def add_documento_tramite(self, form_data: dict):
        new_documento_tramite_name = form_data.get(
            "new_documento_tramite_name", ""
        ).strip()
        if not self.selected_tipo_tramite_id:
            return rx.toast.error("Selecciona un tipo de trámite.")
        if not new_documento_tramite_name:
            return rx.toast.error("El nombre del documento no puede estar vacío.")
        try:
            client = get_db_client()
            client.table("documentos_tramite").insert(
                {
                    "tipo_tramite_id": int(self.selected_tipo_tramite_id),
                    "nombre_documento": new_documento_tramite_name,
                }
            ).execute()
            yield rx.toast.success("Documento añadido al trámite.")
            yield State.load_documentos_tramite(self.selected_tipo_tramite_id)
        except Exception as e:
            logging.exception(f"Error al añadir documento de trámite: {e}")
            return rx.toast.error("Error al añadir documento.")

    @rx.event(background=True)
    async def load_documentos_tramite(self, tipo_tramite_id: str):
        async with self:
            self.selected_tipo_tramite_id = tipo_tramite_id
            self.documentos_tramite = []
            self.new_tramite_tipo_id = tipo_tramite_id
            self.new_tramite_documentos_seleccionados = {}
        if not tipo_tramite_id:
            return
        try:
            client = get_db_client()
            if not client:
                return rx.toast.error("No se pudo conectar a la base de datos.")
            response = (
                client.table("documentos_tramite")
                .select("id, nombre_documento")
                .eq("tipo_tramite_id", int(tipo_tramite_id))
                .order("nombre_documento")
                .execute()
            )
            async with self:
                docs = response.data
                self.documentos_tramite = docs
                self.new_tramite_documentos_seleccionados = {
                    str(doc["id"]): False for doc in docs
                }
        except Exception as e:
            logging.exception(f"Error al cargar documentos de trámite: {e}")
            return rx.toast.error("Error de red al cargar documentos.")

    @rx.event
    def add_documento_enfriador(self, form_data: dict):
        new_documento_enfriador_name = form_data.get(
            "new_documento_enfriador_name", ""
        ).strip()
        if not new_documento_enfriador_name:
            return rx.toast.error("El nombre del documento no puede estar vacío.")
        try:
            client = get_db_client()
            client.table("documentos_enfriadores").insert(
                {"nombre_documento": new_documento_enfriador_name}
            ).execute()
            yield rx.toast.success("Documento para enfriadores añadido.")
            yield State.load_documentos_enfriadores
        except Exception as e:
            logging.exception(f"Error al añadir documento para enfriador: {e}")
            return rx.toast.error("Error al añadir documento. ¿Ya existe?")

    @rx.event(background=True)
    async def load_documentos_enfriadores(self):
        try:
            client = get_db_client()
            if not client:
                return rx.toast.error("No se pudo conectar a la base de datos.")
            response = (
                client.table("documentos_enfriadores")
                .select("id, nombre_documento")
                .order("nombre_documento")
                .execute()
            )
            async with self:
                self.documentos_enfriadores = response.data
        except Exception as e:
            logging.exception(f"Error al cargar documentos de enfriadores: {e}")
            async with self:
                self.documentos_enfriadores = []
            return rx.toast.error("Error de red al cargar documentos de enfriadores.")

    @rx.event(background=True)
    async def buscar_cliente(self):
        if not self.new_tramite_cliente_numero:
            async with self:
                self.new_tramite_cliente_data = None
            return
        try:
            client = get_db_client()
            if not client:
                return rx.toast.error("No se pudo conectar a la base de datos.")
            response = (
                client.table("clientes")
                .select(
                    "numero_cliente, nombre, frecuencia_entrega, frecuencia_preventa"
                )
                .eq("numero_cliente", self.new_tramite_cliente_numero)
                .maybe_single()
                .execute()
            )
            async with self:
                self.new_tramite_cliente_data = response.data
        except Exception as e:
            logging.exception(f"Error al buscar cliente: {e}")
            async with self:
                self.new_tramite_cliente_data = None
            return rx.toast.error("Error de red al buscar cliente.")

    @rx.event
    def toggle_documento_seleccionado(self, doc_id: str):
        doc_id_str = str(doc_id)
        self.new_tramite_documentos_seleccionados[
            doc_id_str
        ] = not self.new_tramite_documentos_seleccionados.get(doc_id_str, False)

    @rx.event
    def guardar_tramite(self):
        if not all(
            [
                self.new_tramite_tipo_id,
                self.new_tramite_cliente_data,
                self.new_tramite_contacto,
                self.new_tramite_fecha,
            ]
        ):
            return rx.toast.error("Por favor, complete todos los campos obligatorios.")
        try:
            client = get_db_client()
            tramite_data = {
                "tipo_tramite_id": int(self.new_tramite_tipo_id),
                "cliente_numero": self.new_tramite_cliente_data["numero_cliente"],
                "numero_contacto": self.new_tramite_contacto,
                "fecha": self.new_tramite_fecha,
                "comentarios": self.new_tramite_comentarios,
                "estatus": self.new_tramite_estatus,
            }
            response = client.table("tramites").insert(tramite_data).execute()
            tramite_id = response.data[0]["id"]
            docs_to_insert = []
            for (
                doc_id,
                seleccionado,
            ) in self.new_tramite_documentos_seleccionados.items():
                if seleccionado:
                    docs_to_insert.append(
                        {"tramite_id": tramite_id, "documento_tramite_id": int(doc_id)}
                    )
            if docs_to_insert:
                client.table("tramites_documentos").insert(docs_to_insert).execute()
            self.new_tramite_tipo_id = ""
            self.new_tramite_cliente_numero = ""
            self.new_tramite_cliente_data = None
            self.new_tramite_contacto = ""
            self.new_tramite_fecha = ""
            self.new_tramite_comentarios = ""
            self.new_tramite_estatus = "RECIBIDO"
            self.new_tramite_documentos_seleccionados = {}
            self.documentos_tramite = []
            yield rx.toast.success("Trámite guardado con éxito.")
            yield State.load_tramites
        except Exception as e:
            logging.exception(f"Error al guardar el trámite: {e}")
            return rx.toast.error("Ocurrió un error al guardar el trámite.")

    @rx.event(background=True)
    async def load_tramites(self):
        async with self:
            self.tramites = []
        try:
            client = get_db_client()
            if not client:
                logging.error("load_tramites: Database client is not available.")
                return rx.toast.error("No se pudo conectar a la base de datos.")
            rpc_params = {}
            if self.filtro_estatus:
                rpc_params["p_estatus"] = self.filtro_estatus
            else:
                rpc_params["p_estatus"] = None
            response = client.rpc("get_tramites_filtrados", rpc_params).execute()
            async with self:
                if response.data:
                    self.tramites = response.data
                else:
                    self.tramites = []
        except Exception as e:
            logging.exception(f"Error al cargar los trámites: {e}")
            async with self:
                self.tramites = []
            return rx.toast.error("Error de red al cargar trámites.")

    @rx.event
    def set_page(self, page: str):
        """Set the current page."""
        self.current_page = page
        if page == "Trámites":
            return State.load_tramites

    @rx.event
    def set_new_tramite_tipo_id(self, value: str):
        self.new_tramite_tipo_id = value

    @rx.event
    def set_new_tramite_cliente_numero(self, value: str):
        self.new_tramite_cliente_numero = value

    @rx.event
    def set_new_tramite_contacto(self, value: str):
        self.new_tramite_contacto = value

    @rx.event
    def set_new_tramite_fecha(self, value: str):
        self.new_tramite_fecha = value

    @rx.event
    def set_new_tramite_comentarios(self, value: str):
        self.new_tramite_comentarios = value

    @rx.event
    def set_new_tramite_estatus(self, value: str):
        self.new_tramite_estatus = value

    @rx.event
    def set_filtro_estatus(self, value: str):
        self.filtro_estatus = value

    @rx.var
    def page_title(self) -> str:
        """Return the current page title."""
        return self.current_page.capitalize()