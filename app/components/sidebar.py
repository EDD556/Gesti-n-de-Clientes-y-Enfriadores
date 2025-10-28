import reflex as rx
from app.state import State


def nav_item(item: dict) -> rx.Component:
    """A single navigation item."""
    is_active = State.current_page == item["name"]
    return rx.el.a(
        rx.el.div(
            rx.icon(
                item["icon"],
                class_name=rx.cond(
                    is_active,
                    "text-orange-500",
                    "text-gray-500 group-hover:text-gray-800",
                ),
            ),
            rx.el.span(
                item["name"],
                class_name=rx.cond(
                    is_active,
                    "font-semibold text-gray-800",
                    "font-medium text-gray-600 group-hover:text-gray-800",
                ),
            ),
            rx.el.div(
                class_name=rx.cond(
                    is_active,
                    "absolute left-0 top-0 h-full w-1 bg-orange-500 rounded-r-md",
                    "",
                )
            ),
            class_name="flex items-center gap-4 p-4 rounded-lg relative cursor-pointer group",
            on_click=lambda: State.set_page(item["name"]),
        ),
        href=item["route"],
        class_name=rx.cond(
            is_active, "bg-orange-50 w-full", "w-full hover:bg-gray-100"
        ),
        width="100%",
    )


def sidebar() -> rx.Component:
    """The sidebar component."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("package-2", size=32, class_name="text-orange-600"),
                rx.el.h1(
                    "Gestión Trámites", class_name="text-2xl font-bold text-gray-800"
                ),
                class_name="flex items-center gap-4 h-16 px-6 border-b border-gray-200 shadow-sm",
            ),
            rx.el.nav(
                rx.foreach(State.nav_items, nav_item),
                class_name="flex flex-col gap-2 p-4",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name="w-64 border-r bg-white font-['JetBrains_Mono'] shadow-md",
        style={"box-shadow": "0px 1px 3px rgba(0,0,0,0.12)"},
    )