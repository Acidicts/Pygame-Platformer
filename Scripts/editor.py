import sys

import pygame

from Scripts.utils import load_images
from Scripts.tilemap import Tile_map

RENDER_SCALE = 2.0


class Editor:
    def __init__(self, map):
        pygame.init()

        pygame.display.set_caption("Platformer Editor")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        self.map = map

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'power_ups': load_images('power_ups'),
            'spawners': load_images('tiles/spawners'),
        }

        self.movement = [False, False, False, False]

        self.tile_map = Tile_map(self, tile_size=16)

        try:
            self.tile_map.load('Assets/maps/{}.json'.format(str(self.map)))
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]

        self.right_clicking = False
        self.clicking = False
        self.shift = False

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.on_grid = True

    def run(self):
        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tile_map.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tile_map.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tile_map.tile_size))

            if self.on_grid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tile_map.tile_size - self.scroll[0],
                                                     tile_pos[1] * self.tile_map.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)

            if self.clicking and self.on_grid:
                tile = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
                self.tile_map.tile_map[str(tile_pos[0]) + ';' + str(tile_pos[1])] = tile
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tile_map.tile_map:
                    del self.tile_map.tile_map[tile_loc]
                for tile in self.tile_map.off_grid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1],
                                         tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tile_map.off_grid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.on_grid:
                            self.tile_map.off_grid_tiles.append({'type': self.tile_list[self.tile_group],
                                                                 'variant': self.tile_variant,
                                                                 'pos': (mpos[0] + self.scroll[0],
                                                                         mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = ((self.tile_variant - 1) %
                                                 len(self.assets[self.tile_list[self.tile_group]]))
                        if event.button == 5:
                            self.tile_variant = ((self.tile_variant + 1) %
                                                 len(self.assets[self.tile_list[self.tile_group]]))
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.on_grid = not self.on_grid
                    if event.key == pygame.K_t:
                        self.tile_map.autotile()
                    if event.key == pygame.K_o:
                        self.tile_map.save('Assets/maps/{}.json'.format(str(self.map)))
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_s or event.key == pygame.K_UP:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Editor(map=input("Choose map # \n")).run()
