import reflex as rx
from app.components.main_layout import main_layout
from app.state import State, Cliente


def _cliente_info_card(cliente: rx.Var[Cliente]) -> rx.Component:
    return rx.el.div(
        rx.el.h4("Datos del Cliente", class_name="font-semibold text-gray-700 mb-2"),
        rx.el.p(f"Nombre: {cliente['nombre']}", class_name="text-sm text-gray-600"),
        rx.el.p(
            f"Frec. Entrega: {cliente['frecuencia_entrega']}",
            class_name="text-sm text-gray-600",
        ),
        rx.el.p(
            f"Frec. Preventa: {cliente['frecuencia_preventa']}",
            class_name="text-sm text-gray-600",
        ),
        class_name="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200",
    )


def _documentos_checklist() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Documentos Requeridos", class_name="font-semibold text-gray-700 mb-2"
        ),
        rx.el.div(
            rx.foreach(
                State.documentos_tramite,
                lambda doc: rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        on_change=lambda: State.toggle_documento_seleccionado(
                            doc["id"]
                        ),
                        checked=State.new_tramite_documentos_seleccionados[
                            doc["id"].to_string()
                        ],
                        class_name="mr-2 rounded border-gray-300 text-orange-600 focus:ring-orange-500",
                    ),
                    doc["nombre_documento"],
                    class_name="flex items-center text-sm text-gray-600",
                ),
            ),
            class_name="space-y-2",
        ),
        class_name="mt-4",
    )


def _nuevo_tramite_form() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Nuevo Trámite", class_name="text-2xl font-bold text-gray-800 mb-6"),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Tipo de Trámite",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.select(
                    rx.el.option("Selecciona un tipo", value="", disabled=True),
                    rx.foreach(
                        State.tipos_tramite,
                        lambda tramite: rx.el.option(
                            tramite["nombre"], value=tramite["id"]
                        ),
                    ),
                    on_change=State.load_documentos_tramite,
                    value=State.new_tramite_tipo_id,
                    class_name="w-full p-2 border rounded-md shadow-sm",
                ),
                class_name="w-full md:w-1/2",
            ),
            rx.el.div(
                rx.el.label(
                    "Número de Cliente",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="Buscar por número de cliente",
                    on_change=State.set_new_tramite_cliente_numero,
                    on_blur=State.buscar_cliente,
                    class_name="w-full p-2 border rounded-md shadow-sm",
                    default_value=State.new_tramite_cliente_numero,
                ),
                class_name="w-full md:w-1/2",
            ),
            class_name="flex flex-col md:flex-row gap-4 mb-4",
        ),
        rx.cond(
            State.new_tramite_cliente_data,
            _cliente_info_card(State.new_tramite_cliente_data),
            None,
        ),
        rx.cond(State.new_tramite_tipo_id != "", _documentos_checklist(), None),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Número de Contacto",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    placeholder="Teléfono de contacto",
                    on_change=State.set_new_tramite_contacto,
                    class_name="w-full p-2 border rounded-md shadow-sm",
                    default_value=State.new_tramite_contacto,
                ),
                class_name="w-full md:w-1/2",
            ),
            rx.el.div(
                rx.el.label(
                    "Fecha", class_name="block text-sm font-medium text-gray-700 mb-1"
                ),
                rx.el.input(
                    type="date",
                    on_change=State.set_new_tramite_fecha,
                    class_name="w-full p-2 border rounded-md shadow-sm",
                    default_value=State.new_tramite_fecha,
                ),
                class_name="w-full md:w-1/2",
            ),
            class_name="flex flex-col md:flex-row gap-4 my-4",
        ),
        rx.el.div(
            rx.el.label(
                "Comentarios", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.textarea(
                placeholder="Añade comentarios adicionales aquí...",
                on_change=State.set_new_tramite_comentarios,
                class_name="w-full p-2 border rounded-md shadow-sm",
                default_value=State.new_tramite_comentarios,
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Estatus", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.select(
                rx.foreach(
                    State.estatus_options,
                    lambda estatus: rx.el.option(estatus, value=estatus),
                ),
                value=State.new_tramite_estatus,
                on_change=State.set_new_tramite_estatus,
                class_name="w-full p-2 border rounded-md shadow-sm",
            ),
            class_name="w-full md:w-1/3 mb-6",
        ),
        rx.el.button(
            rx.icon("save", class_name="mr-2"),
            "Guardar Trámite",
            on_click=State.guardar_tramite,
            class_name="flex items-center px-6 py-3 bg-orange-500 text-white rounded-md shadow-md hover:bg-orange-600 font-semibold",
        ),
        class_name="p-6 bg-white rounded-lg shadow-sm mb-8",
    )


def _tramites_table() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Historial de Trámites", class_name="text-2xl font-bold text-gray-800 mb-4"
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("Todos los estatus", value=""),
                rx.foreach(State.estatus_options, lambda o: rx.el.option(o, value=o)),
                on_change=State.set_filtro_estatus,
                value=State.filtro_estatus,
                class_name="p-2 border rounded-md shadow-sm",
            ),
            rx.el.button(
                "Filtrar",
                on_click=State.load_tramites,
                class_name="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 font-medium",
            ),
            class_name="flex items-center gap-4 mb-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "ID",
                            class_name="p-3 text-left text-sm font-semibold text-gray-600",
                        ),
                        rx.el.th(
                            "Tipo Trámite",
                            class_name="p-3 text-left text-sm font-semibold text-gray-600",
                        ),
                        rx.el.th(
                            "Cliente",
                            class_name="p-3 text-left text-sm font-semibold text-gray-600",
                        ),
                        rx.el.th(
                            "Contacto",
                            class_name="p-3 text-left text-sm font-semibold text-gray-600",
                        ),
                        rx.el.th(
                            "Fecha",
                            class_name="p-3 text-left text-sm font-semibold text-gray-600",
                        ),
                        rx.el.th(
                            "Estatus",
                            class_name="p-3 text-left text-sm font-semibold text-gray-600",
                        ),
                    ),
                    class_name="bg-gray-50 border-b border-gray-200",
                ),
                rx.el.tbody(
                    rx.foreach(
                        State.tramites,
                        lambda tramite: rx.el.tr(
                            rx.el.td(
                                tramite["id"], class_name="p-3 text-sm text-gray-700"
                            ),
                            rx.el.td(
                                tramite["tipo_tramite_nombre"],
                                class_name="p-3 text-sm text-gray-700",
                            ),
                            rx.el.td(
                                tramite["cliente_nombre"],
                                class_name="p-3 text-sm text-gray-700",
                            ),
                            rx.el.td(
                                tramite["numero_contacto"],
                                class_name="p-3 text-sm text-gray-700",
                            ),
                            rx.el.td(
                                tramite["fecha"], class_name="p-3 text-sm text-gray-700"
                            ),
                            rx.el.td(
                                rx.el.span(
                                    tramite["estatus"],
                                    class_name=rx.match(
                                        tramite["estatus"],
                                        (
                                            "RECIBIDO",
                                            "bg-blue-100 text-blue-800 px-2 py-1 text-xs font-medium rounded-full w-fit",
                                        ),
                                        (
                                            "RECHAZADO",
                                            "bg-red-100 text-red-800 px-2 py-1 text-xs font-medium rounded-full w-fit",
                                        ),
                                        (
                                            "EN PROCESO",
                                            "bg-yellow-100 text-yellow-800 px-2 py-1 text-xs font-medium rounded-full w-fit",
                                        ),
                                        (
                                            "PENDIENTE DE ENTREGA",
                                            "bg-purple-100 text-purple-800 px-2 py-1 text-xs font-medium rounded-full w-fit",
                                        ),
                                        (
                                            "ENTREGADO",
                                            "bg-green-100 text-green-800 px-2 py-1 text-xs font-medium rounded-full w-fit",
                                        ),
                                        "bg-gray-100 text-gray-800 px-2 py-1 text-xs font-medium rounded-full w-fit",
                                    ),
                                ),
                                class_name="p-3 text-sm",
                            ),
                            class_name="border-b border-gray-200 hover:bg-gray-50",
                        ),
                    )
                ),
            ),
            class_name="overflow-x-auto w-full bg-white rounded-lg shadow-sm border",
        ),
    )


def tramites_page() -> rx.Component:
    """The procedures page."""
    return main_layout(
        rx.el.div(
            _nuevo_tramite_form(),
            _tramites_table(),
            on_mount=[State.load_tipos_tramite],
        )
    )