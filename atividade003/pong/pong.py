import random
from winsound import PlaySound, SND_ASYNC
from objects import (
    main_menu,
    setup_screen,
    create_paddle,
    create_ball,
    create_hud
)
from controls import bind_controls


# area constants
TOP_LIMIT = 290
BOTTOM_LIMIT = -290
LEFT_LIMIT = -390
RIGHT_LIMIT = 390

# game constants
MAX_SPEED_X = 6.0
MAX_SPEED_Y = 6.0
INCREASE_FACTOR = 1.1
FPS = 60
TIMER_INTERVAL = int(1000 / FPS)  # 17ms for ~60 FPS

# config variables 
paused = {"value": False}

def game_loop(screen, paddle_1, paddle_2, ball, hud, score_1, score_2, paused):
    def loop():
        try:
            nonlocal score_1, score_2
            if not paused["value"]:
                screen.update()
                ball.setx(ball.xcor() + ball.dx)
                ball.sety(ball.ycor() + ball.dy)

                # collision with top wall
                if ball.ycor() + 10 > 290:
                    PlaySound("assets/bounce.wav", SND_ASYNC)
                    ball.sety(280)
                    ball.dy *= -1
                # collision with bottom wall
                if ball.ycor() - 10 < -290:
                    PlaySound("assets/bounce.wav", SND_ASYNC)
                    ball.sety(-280)
                    ball.dy *= -1

                # collision with left wall
                if ball.xcor() - 10 < -390:
                    score_2 += 1
                    hud.clear()
                    hud.write(
                        f"{score_1} : {score_2}", align="center",
                        font=("Press Start 2P", 24, "normal")
                    )
                    PlaySound(
                        "assets/258020__kodack__arcade-bleep-sound.wav",
                        SND_ASYNC
                    )
                    ball.goto(0, 0)
                    ball.dx = 4
                    ball.dy = random.uniform(-4, 4) # random angle

                # collision with right wall
                if ball.xcor() + 10 > 390:
                    score_1 += 1
                    hud.clear()
                    hud.write(
                        f"{score_1} : {score_2}", align="center",
                        font=("Press Start 2P", 24, "normal")
                    )
                    PlaySound(
                        "assets/258020__kodack__arcade-bleep-sound.wav",
                        SND_ASYNC
                    )
                    ball.goto(0, 0)
                    ball.dx = -4
                    ball.dy = random.uniform(-4, 4) # random angle

                # left paddle (paddle_1)
                if ball.xcor() < -330 and paddle_1.ycor() + 50 >= ball.ycor() >= paddle_1.ycor() - 50:
                    ball.setx(-330)
                    ball.dx *= -1
                    PlaySound("assets/bounce.wav", SND_ASYNC)

                    offset = ball.ycor() - paddle_1.ycor()
                    ball.dy += offset * 0.07

                    if -0.5 < ball.dy < 0.5:
                        if ball.dy >= 0:
                            ball.dy = random.uniform(0.5, 1.5)
                        else:
                            ball.dy = random.uniform(-1.5, -0.5)

                    VELOCIDADE_MAX_Y = 6.0 
                    if ball.dy > VELOCIDADE_MAX_Y:
                        ball.dy = VELOCIDADE_MAX_Y
                    elif ball.dy < -VELOCIDADE_MAX_Y:
                        ball.dy = -VELOCIDADE_MAX_Y

                    FATOR_AUMENTO = 1.1
                    ball.dx *= FATOR_AUMENTO
                    ball.dy *= FATOR_AUMENTO

                # right paddle (paddle_2)
                if ball.xcor() > 330 and paddle_2.ycor() + 50 >= ball.ycor() >= paddle_2.ycor() - 50:
                    ball.setx(330)
                    ball.dx *= -1
                    PlaySound("assets/bounce.wav", SND_ASYNC)
                    
                    offset = ball.ycor() - paddle_2.ycor()
                    ball.dy += offset * 0.07

                    if -0.5 < ball.dy < 0.5:
                        if ball.dy >= 0:
                            ball.dy = random.uniform(0.5, 1.5)
                        else:
                            ball.dy = random.uniform(-1.5, -0.5)

                    VELOCIDADE_MAX_Y = 6.0
                    if ball.dy > VELOCIDADE_MAX_Y:
                        ball.dy = VELOCIDADE_MAX_Y
                    elif ball.dy < -VELOCIDADE_MAX_Y:
                        ball.dy = -VELOCIDADE_MAX_Y

                    FATOR_AUMENTO = 1.1
                    ball.dx *= FATOR_AUMENTO
                    ball.dy *= FATOR_AUMENTO

                VELOCIDADE_MAX_X = 6.0
                if ball.dx > VELOCIDADE_MAX_X:
                    ball.dx = VELOCIDADE_MAX_X
                elif ball.dx < -VELOCIDADE_MAX_X:
                    ball.dx = -VELOCIDADE_MAX_X

            screen.ontimer(loop, 17)  # 60 FPS
        except Exception as e:
            import turtle
            if isinstance(e, turtle.Terminator):
                pass  # ignore if window is closed
            else:
                raise
    loop()

def main():
    try:
        screen = setup_screen()

        main_menu(screen)

        paddle_1 = create_paddle(-350)
        paddle_2 = create_paddle(350)
        ball = create_ball()
        hud = create_hud()
        score_1 = 0
        score_2 = 0

        bind_controls(screen, paddle_1, paddle_2, paused)
        game_loop(screen, paddle_1, paddle_2, ball, hud, score_1, score_2, paused)
        screen.mainloop()
    except Exception :
        pass
    
if __name__ == "__main__":
    main()