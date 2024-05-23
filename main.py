# https://stackoverflow.com/questions/53930305/nodemon-error-system-limit-for-number-of-file-watchers-reached
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from nicegui import ui, app
import requests


env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

def get_chat_response(prompt):
    response = requests.post(
    url="http://127.0.0.1:5000/v1/chat/completions",
    json={
        "model": "google_gemma-1.1-2b-it",
        "messages": [{ "role": "user", "content": prompt}],
        "stream": False
        }
    )
    answer = response.json()['choices'][0]['message']['content']
    return answer

def get_personality_file(value):
    match value:
        case "Default":
            return "default.jinja"
        case "Santa Claus":
            return "santaclaus.jinja"
        case "Scientist":
            return "scientist.jinja"
        case _:
            return "default.jinja"

def send():
    user_prompt = app.storage.client.get("prompt")
    personality = app.storage.client.get("personality")

    personality_template = env.get_template((get_personality_file(personality)))
    prompt_template = env.get_template("prompt.jinja")

    prompt = prompt_template.render(
        prompt = user_prompt,
        personality = personality_template.render()
    )

    ui.notify("Sending to Gemma ...", type="info")
    answer = get_chat_response(prompt)
    ui.notify("Received response ...", type="info")
    app.storage.client["response"] =  answer
    


@ui.page("/")
def index():
    with ui.grid(columns=16).classes("w-3/4 place-self-center gap-4"):
        ui.markdown("# Gemma Chatbot").classes("col-span-full")
        ui.input(label="Prompt").bind_value(app.storage.client, "prompt").classes("col-span-10")
        
        ui.select(
            options=["Default", "Santa Claus", "Scientist"],
            value="Default",
            label="Personality"
        ).bind_value(app.storage.client, "personality").classes("col-span-6")
        ui.button("Send to Gemma", on_click=send).classes("col-span-8")

        dark = ui.dark_mode()
        ui.button("Light UI", on_click=dark.disable).classes("col-span-4")
        ui.button("Dark UI", on_click=dark.enable).classes("col-span-4")
        with ui.card().classes("col-span-full"):
            ui.markdown("## Gemma Response")
            ui.separator()
            ui.label().bind_text(app.storage.client, "response")
ui.run()

