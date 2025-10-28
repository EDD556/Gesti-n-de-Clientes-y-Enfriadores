import reflex as rx
from app.pages.configuracion import configuracion_page
from app.pages.enfriadores import enfriadores_page
from app.pages.tramites import tramites_page
from app.state import State

app = rx.App(
    theme=rx.theme(appearance="light", accent_color="orange"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(
    configuracion_page,
    route="/",
    on_load=[State.initialize_app, lambda: State.set_page("Configuraci\x97n")],
)
app.add_page(
    enfriadores_page,
    route="/enfriadores",
    on_load=lambda: State.set_page("Enfriadores"),
)
app.add_page(
    tramites_page,
    route="/tramites",
    on_load=[State.load_tramites, lambda: State.set_page("Trámites")],
)