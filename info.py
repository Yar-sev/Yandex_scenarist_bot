import json
def informat(id, command):
    with open('data.json') as f:
        data = json.load(f)
    inf = {'/start': f"""Привет {data['users'][str(id)][0]}!
это квест-бот
для начала игры - /quest
для доп. информации - /help""",
           '/help' : f"""допю информация:
/start - при первом запуске
/quest - для начала игрв
/help - доп информация"""}
    return inf[command]