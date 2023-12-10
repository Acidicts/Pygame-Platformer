import pygame

class Hud:
    def __init__(self, game):
        pygame.init()

        self.hearts = game.lives
        self.game = game

    def draw(self):
        self.game.hud_display.blit(self.game.assets['heart'], (0, 0))

    def update(self):
        self.draw()