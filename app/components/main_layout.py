import reflex as rx
from app.components.sidebar import sidebar
from app.state import State


def main_layout(child: rx.Component) -> rx.Component:
    """The main layout for the app."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.header(
                    rx.el.h1(
                        State.page_title, class_name="text-3xl font-bold text-gray-800"
                    ),
                    class_name="p-6 border-b border-gray-200 bg-white rounded-lg mb-6",
                    style={"box-shadow": "0px 1px 3px rgba(0,0,0,0.08)"},
                ),
                child,
                class_name="p-6",
            ),
            class_name="flex-1 bg-gray-50 overflow-y-auto",
        ),
        class_name="flex h-screen w-screen bg-white font-['JetBrains_Mono']",
    )