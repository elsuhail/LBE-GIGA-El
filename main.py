from __future__ import annotations

import pygame

from audio import AudioManager
from config import APP
from game_state import GameState, Phase
from states.encounter import EncounterState
from states.game_over import GameOverState
from states.menu import MenuState
from states.shop import ShopState
from ui import FontSet


def main() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((APP.width, APP.height), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption(APP.title)
    clock = pygame.time.Clock()
    fonts = FontSet.default()
    state = GameState()  # Satu run dipakai bersama antar state.
    audio = AudioManager()
    menu = MenuState(screen, fonts, audio)
    encounter = EncounterState(screen, fonts, state, audio)
    shop = ShopState(screen, fonts, state, audio)
    game_over = GameOverState(screen, fonts, state, audio)

    phase = Phase.MENU
    while True:
        if phase == Phase.MENU:
            audio.play_bgm("menu")
            if menu.run(clock) == "start":
                state.start_run()
                phase = Phase.ENCOUNTER
            else:
                break
        elif phase == Phase.ENCOUNTER:
            audio.play_bgm("encounter")
            result = encounter.run(clock)
            if result == "shop":
                phase = Phase.SHOP
            elif result == "game_over":
                phase = Phase.GAME_OVER
            else:
                break
        elif phase == Phase.SHOP:
            audio.play_bgm("shop")
            if shop.run(clock) == "encounter":
                phase = Phase.ENCOUNTER
            else:
                break
        elif phase == Phase.GAME_OVER:
            audio.play_bgm("gameover")
            result = game_over.run(clock)
            if result == "restart":
                state.start_run()
                phase = Phase.ENCOUNTER
            elif result == "menu":
                phase = Phase.MENU
            else:
                break
    pygame.quit()


if __name__ == "__main__":
    main()
