import turtle


def setup_screen():
    screen = turtle.Screen()
    screen.title("My Pong")
    screen.bgcolor("black")
    screen.setup(width=800, height=600)
    screen.tracer(0)

    return screen


def create_hud():
    hud = turtle.Turtle()
    hud.speed(0)
    hud.shape("square")
    hud.color("white")
    hud.penup()
    hud.hideturtle()
    hud.goto(0, 260)
    hud.write("0 : 0", align="center",
              font=("Press Start 2P", 24, "normal"))

    return hud


def create_paddle(pos_x: int):
    paddle = turtle.Turtle()
    paddle.speed(0)
    paddle.shape("square")
    paddle.color("white")
    paddle.shapesize(stretch_wid=5, stretch_len=1)
    paddle.penup()
    paddle.goto(pos_x, 0)

    return paddle


def create_ball():
    ball = turtle.Turtle()
    ball.speed(0)
    ball.shape("square")
    ball.color("white")
    ball.penup()
    ball.goto(0, 0)
    ball.dx = 4
    ball.dy = 4

    return ball


def show_credits(screen, back_callback):
    credits_turtle = turtle.Turtle()
    credits_turtle.hideturtle()
    credits_turtle.color("white")
    credits_turtle.penup()
    credits_turtle.goto(0, 150)
    credits_turtle.write(
        "Credits",
        align="center",
        font=("Arial", 32, "bold")
    )
    credits_turtle.goto(0, 0)
    credits_turtle.write(
        "Valdenei Junior\nRanielly Barroso\nCaio Chaul",
        align="center",
        font=("Arial", 18, "normal")
    )
    credits_turtle.goto(0, -80)
    credits_turtle.write(
        "Press ESC to go back",
        align="center",
        font=("Arial", 16, "normal")
    )

    def back_to_menu():
        credits_turtle.clear()
        screen.onkeypress(None, "Escape")
        screen.onkeypress(None, "Return")
        back_callback()

    screen.onkeypress(back_to_menu, "Escape")
    screen.onkeypress(None, "Return")


def main_menu(screen):
    title_turtle = turtle.Turtle()
    title_turtle.hideturtle()
    title_turtle.color("white")
    title_turtle.penup()
    title_turtle.goto(0, 80)
    title_turtle.write(
        "PONG",
        align="center",
        font=("Arial", 40, "bold")
    )

    menu_turtle = turtle.Turtle()
    menu_turtle.hideturtle()
    menu_turtle.color("white")
    menu_turtle.penup()
    menu_turtle.goto(0, 10)
    menu_turtle.write(
        "Press Enter to start",
        align="center",
        font=("Arial", 24, "normal")
    )

    credits_turtle = turtle.Turtle()
    credits_turtle.hideturtle()
    credits_turtle.color("white")
    credits_turtle.penup()
    credits_turtle.goto(0, -60)
    credits_turtle.write(
        "Press 'C' to view credits",
        align="center",
        font=("Arial", 18, "normal")
    )

    started = {"value": False}

    def redraw_menu():
        title_turtle.clear()
        menu_turtle.clear()
        credits_turtle.clear()
        title_turtle.goto(0, 80)
        title_turtle.write(
            "PONG",
            align="center",
            font=("Arial", 40, "bold")
        )
        menu_turtle.goto(0, 10)
        menu_turtle.write(
            "Press Enter to start",
            align="center",
            font=("Arial", 24, "normal")
        )
        credits_turtle.goto(0, -60)
        credits_turtle.write(
            "Press 'C' to view credits",
            align="center",
            font=("Arial", 18, "normal")
        )
        screen.onkeypress(start_game, "Return")

    def start_game():
        title_turtle.clear()
        menu_turtle.clear()
        credits_turtle.clear()
        screen.onkeypress(None, "Return")
        started["value"] = True

    def show_credits_call():
        title_turtle.clear()
        menu_turtle.clear()
        credits_turtle.clear()
        show_credits(screen, back_callback=redraw_menu)

    screen.listen()
    screen.onkeypress(start_game, "Return")
    screen.onkeypress(show_credits_call, "c")

    while not started["value"]:
        screen.update()
