import reflex as rx
from app.components.main_layout import main_layout


def enfriadores_page() -> rx.Component:
    """The coolers page."""
    return main_layout(
        rx.el.div(
            rx.el.p("Página de Enfriadores. Desde aquí se crearán nuevas solicitudes."),
            class_name="p-6 bg-white rounded-lg shadow-sm",
            style={"box-shadow": "0px 1px 3px rgba(0,0,0,0.05)"},
        )
    )