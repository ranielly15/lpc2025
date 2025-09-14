def paddle_up(paddle):
    """Move the paddle upward within the screen limits."""
    y = paddle.ycor()
    if y < 250:
        y += 25
    else:
        y = 250
    paddle.sety(y)


def paddle_down(paddle):
    """Move the paddle downward within the screen limits."""
    y = paddle.ycor()
    if y > -250:
        y -= 25
    else:
        y = -250
    paddle.sety(y)


def pause_game(paused_flag):
    """Toggle the paused state of the game."""
    paused_flag["value"] = not paused_flag["value"]


def bind_controls(screen, paddle_1, paddle_2, paused_flag):
    """Bind keyboard controls for paddles and pause function."""
    screen.listen()
    screen.onkeypress(lambda: paddle_up(paddle_1), "w")
    screen.onkeypress(lambda: paddle_down(paddle_1), "s")
    screen.onkeypress(lambda: paddle_up(paddle_2), "Up")
    screen.onkeypress(lambda: paddle_down(paddle_2), "Down")
    screen.onkeypress(lambda: pause_game(paused_flag), "space")
