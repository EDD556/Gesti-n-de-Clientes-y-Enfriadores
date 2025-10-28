import reflex as rx
from app.components.main_layout import main_layout
from app.state import State


def _upload_section(
    title: str, description: str, handler: rx.event.EventHandler
) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-xl font-semibold text-gray-700"),
        rx.el.p(description, class_name="text-sm text-gray-500 mt-1 mb-4"),
        rx.upload.root(
            rx.el.div(
                rx.el.p("Arrastra y suelta un archivo aquí"),
                rx.el.p("o", class_name="text-sm text-gray-500"),
                rx.el.button(
                    "Seleccionar Archivo",
                    class_name="mt-2 text-sm font-medium text-orange-600",
                ),
                class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50",
            ),
            id=f"upload-{title.replace(' ', '-').lower()}",
            on_drop=handler,
        ),
        class_name="p-6 bg-white rounded-lg shadow-sm",
        style={"box-shadow": "0px 1px 3px rgba(0,0,0,0.05)"},
    )


def _document_list(documents: rx.Var[list[dict]]) -> rx.Component:
    return rx.el.ul(
        rx.foreach(
            documents,
            lambda doc: rx.el.li(
                rx.icon("file-text", class_name="text-gray-400"),
                doc["nombre_documento"],
                class_name="flex items-center gap-2 p-2 bg-gray-50 rounded-md text-sm",
            ),
        ),
        class_name="flex flex-col gap-2 mt-4",
    )


def _configuracion_tramites() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Tipos de Trámite", class_name="text-xl font-semibold text-gray-700"
            ),
            rx.el.p(
                "Crea nuevos tipos de trámite para el sistema.",
                class_name="text-sm text-gray-500 mt-1 mb-4",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.input(
                        placeholder="Nombre del nuevo trámite",
                        name="new_tipo_tramite_name",
                        class_name="flex-1 p-2 border rounded-md",
                    ),
                    rx.el.button(
                        rx.icon("plus", class_name="mr-2"),
                        "Añadir",
                        type="submit",
                        class_name="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md shadow hover:bg-orange-600",
                    ),
                    class_name="flex items-center gap-2",
                ),
                on_submit=State.add_tipo_tramite,
                reset_on_submit=True,
            ),
            rx.el.ul(
                rx.foreach(
                    State.tipos_tramite,
                    lambda tramite: rx.el.li(
                        tramite["nombre"],
                        class_name="p-2 bg-gray-100 rounded-md text-sm",
                    ),
                ),
                class_name="flex flex-col gap-2 mt-4",
            ),
            class_name="p-6 bg-white rounded-lg shadow-sm",
        ),
        rx.el.div(
            rx.el.h3(
                "Documentos por Trámite",
                class_name="text-xl font-semibold text-gray-700",
            ),
            rx.el.p(
                "Asigna los documentos requeridos a cada tipo de trámite.",
                class_name="text-sm text-gray-500 mt-1 mb-4",
            ),
            rx.el.select(
                rx.el.option("Selecciona un tipo de trámite", value="", disabled=True),
                rx.foreach(
                    State.tipos_tramite,
                    lambda tramite: rx.el.option(
                        tramite["nombre"], value=tramite["id"]
                    ),
                ),
                on_change=State.load_documentos_tramite,
                value=State.selected_tipo_tramite_id,
                class_name="w-full p-2 border rounded-md mb-4",
            ),
            rx.cond(
                State.selected_tipo_tramite_id != "",
                rx.el.div(
                    rx.el.form(
                        rx.el.div(
                            rx.el.input(
                                placeholder="Nombre del nuevo documento",
                                name="new_documento_tramite_name",
                                class_name="flex-1 p-2 border rounded-md",
                            ),
                            rx.el.button(
                                rx.icon("plus", class_name="mr-2"),
                                "Añadir Documento",
                                type="submit",
                                class_name="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md shadow hover:bg-orange-600",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        on_submit=State.add_documento_tramite,
                        reset_on_submit=True,
                    ),
                    _document_list(State.documentos_tramite),
                ),
            ),
            class_name="p-6 bg-white rounded-lg shadow-sm",
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
    )


def _configuracion_enfriadores() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Documentos para Solicitudes de Enfriadores",
            class_name="text-xl font-semibold text-gray-700",
        ),
        rx.el.p(
            "Define los documentos que se pueden requerir en una solicitud de enfriador.",
            class_name="text-sm text-gray-500 mt-1 mb-4",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.input(
                    placeholder="Nombre del nuevo documento",
                    name="new_documento_enfriador_name",
                    class_name="flex-1 p-2 border rounded-md",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="mr-2"),
                    "Añadir Documento",
                    type="submit",
                    class_name="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md shadow hover:bg-orange-600",
                ),
                class_name="flex items-center gap-2",
            ),
            on_submit=State.add_documento_enfriador,
            reset_on_submit=True,
        ),
        _document_list(State.documentos_enfriadores),
        class_name="p-6 bg-white rounded-lg shadow-sm",
    )


def _tab_button(name: str, label: str) -> rx.Component:
    is_active = State.active_config_tab == name
    return rx.el.button(
        label,
        on_click=lambda: State.set_active_config_tab(name),
        class_name=rx.cond(
            is_active,
            "px-4 py-2 text-sm font-semibold text-white bg-orange-500 rounded-md shadow",
            "px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-md",
        ),
    )


def configuracion_page() -> rx.Component:
    """The configuration page with tabs."""
    return main_layout(
        rx.el.div(
            rx.el.div(
                _tab_button("clientes", "Cargar Clientes"),
                _tab_button("enfriadores", "Cargar Enfriadores"),
                _tab_button("tramites", "Configurar Trámites"),
                _tab_button("docs_enfriadores", "Docs. Enfriadores"),
                class_name="flex items-center gap-2 p-2 bg-gray-100 rounded-lg mb-6",
            ),
            rx.match(
                State.active_config_tab,
                (
                    "clientes",
                    _upload_section(
                        "Cargar Datos de Clientes",
                        "Sube un archivo Excel (.xlsx) con las columnas: numero_cliente, nombre, frecuencia_entrega, frecuencia_preventa.",
                        State.handle_clientes_upload,
                    ),
                ),
                (
                    "enfriadores",
                    _upload_section(
                        "Cargar Datos de Enfriadores",
                        "Sube un archivo Excel (.xlsx) con las columnas: canal, serie, modelo.",
                        State.handle_enfriadores_upload,
                    ),
                ),
                ("tramites", _configuracion_tramites()),
                ("docs_enfriadores", _configuracion_enfriadores()),
                rx.el.p("Selecciona una opción de configuración."),
            ),
            class_name="w-full",
        )
    )