import guizero

PLAYERS = sorted(["Marco", "Gladstone", "Junior", "Lidia", "Alex", "Mari"])
PLAYERS_IN = []
PLAYERS_NAMES = []
PLAYERS_TEXTBOXES = []
PLAYERS_POINTS = []
TEXTS = []


def new_game():
    APP.hide()
    PLAYERS_IN.clear()
    for name, textbox in zip(PLAYERS_NAMES, PLAYERS_TEXTBOXES):
        name.destroy()
        textbox.destroy()
    PLAYERS_NAMES.clear()
    PLAYERS_TEXTBOXES.clear()
    PLAYERS_POINTS.clear()
    for text in TEXTS:
        text.destroy()
    TEXTS.clear()
    NEW_MATCH_BUTTON.destroy()
    WINDOW1.show()
    PLAYER_CONFIRM_BUTTON.focus()
    

def confirm_players():
    for checkbox in PLAYERS_CHECKBOXES:
        if checkbox.value:
            PLAYERS_IN.append(checkbox.text)
    if len(PLAYERS_IN) == 0:
        SELECT_PLAYER.value = "Nenhum jogador selecionado"
        SELECT_PLAYER.text_color = "red"
        return
    elif len(PLAYERS_IN) == 1:
        SELECT_PLAYER.value = "Apenas 1 jogador selecionado"
        SELECT_PLAYER.text_color = "red"
        PLAYERS_IN.clear()
        return
    SELECT_PLAYER.value = "Selecione os jogadores"
    SELECT_PLAYER.text_color = "black"
    WINDOW1.hide()
    APP.show()
    create_notepad()


def sum_and_draw():
    points = []
    for name in PLAYERS_NAMES:
        name.text_color = "black"
    for idx, textbox in enumerate(PLAYERS_TEXTBOXES):
        if textbox.value.strip() == "" or not textbox.value.strip().isdigit():
            PLAYERS_NAMES[idx].text_color = "red"
            textbox.focus()
            return
    for idx, textbox in enumerate(PLAYERS_TEXTBOXES):
        PLAYERS_POINTS[idx].append(int(textbox.value.strip()))
        textbox.clear()
    for idx, points in enumerate(PLAYERS_POINTS):
        TEXTS.append(guizero.Text(APP, text=str(sum(points)),
                                  grid=[idx, len(points)+1], align="top"))
        if sum(points) >= 100:
            TEXTS.append(guizero.Text(APP, text="-"*13,
                                      grid=[idx, len(points)+2], align="top"))
            TEXTS.append(guizero.Text(APP, text="BOOM!", color="red",
                                      grid=[idx, len(points)+3], align="top"))
            NEW_MATCH_BUTTON.update_command(new_game)
            NEW_MATCH_BUTTON.image = "new_match_symbol-red-01.png"
    PLAYERS_TEXTBOXES[0].focus()


def create_notepad():
    global NEW_MATCH_BUTTON
    NEW_MATCH_BUTTON = guizero.PushButton(APP, image="new_match_symbol-01.png",
                                          grid=[len(PLAYERS_IN)//2, 900],
                                          align="top", command=sum_and_draw)
    for idx, player in enumerate(PLAYERS_IN):
        PLAYERS_NAMES.append(guizero.Text(APP, text=player, grid=[idx, 0],
                                          align="top"))
        PLAYERS_TEXTBOXES.append(guizero.TextBox(APP, width=8, grid=[idx, 1],
                                                 align="top"))
        PLAYERS_TEXTBOXES[-1].value = "0"
        PLAYERS_POINTS.append([])
    sum_and_draw()


APP = guizero.App(title="Bloquinho do mexe-mexe", layout="grid")
APP.hide()
WINDOW1 = guizero.Window(APP, title="Bloquinho do mexe-mexe", layout="grid")
SELECT_PLAYER = guizero.Text(WINDOW1, text="Selecione os jogadores",
                             grid=[0, 0], align="left")
PLAYERS_CHECKBOXES = []
for idx, player in enumerate(PLAYERS):
    PLAYERS_CHECKBOXES.append(guizero.CheckBox(WINDOW1, text=player,
                                               grid=[0, idx+1], align="left"))
PLAYER_CONFIRM_BUTTON = guizero.PushButton(WINDOW1, text="Confirmar",
                                           grid=[0, len(PLAYERS)+1],
                                           align="top",
                                           command=confirm_players)


APP.display()
