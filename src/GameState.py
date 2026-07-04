import math
from EmberCoreSystem import EmberCoreSystem
from EssenceSystem import EssenceSystem
import ImageManager
import ProgressBar
from MobSystem import MOB_STATS, STAT_DESCRIPTIONS, MobSystem
import pygame
from config import RESOLUTION_OPTIONS
from paths import FONTS

BUTTON_TILE_SIZE = 8
BUTTON_PADDING_X = 12
BUTTON_PADDING_Y = 8
SETTINGS_CONTENT_PADDING = 64
DROPDOWN_WIDTH = 160
DROPDOWN_HEIGHT = 28
CONTROL_GAP = 10
CHECKBOX_SIZE = 24
MENU_BUTTON_HEIGHT = 34
MOB_SPRITE_SIZE = 48
EMBERSTONE_LIFEFORCE_TO_LEVEL = 10
BASE_SUMMON_COST = 10
SUMMON_PREVIEW_CELL_SIZE = 80
MOB_SCROLLBAR_WIDTH = 12
MOB_SCROLLBAR_MIN_THUMB_HEIGHT = 32
MOB_SCROLL_WHEEL_PIXELS = 96
STAT_PROGRESS_BAR_SIZE = (144, 24)
DEBUG_TOGGLE_BUTTON_SIZE = 24
TEXT_COLOR = (20, 20, 20)
ESSENCE_TEXT_COLOR = (245, 240, 220)
RATE_TEXT_COLOR = (90, 150, 210)
GRID_LINE_COLOR = (70, 64, 58)
SELECTED_COLOR = (255, 255, 255)
LIFEFORCE_TEXT_COLOR = (220, 80, 80)
AFFORDABLE_TEXT_COLOR = (95, 220, 105)
UNAFFORDABLE_TEXT_COLOR = (220, 80, 80)
STAR_TEXT_COLOR = (245, 190, 65)
RESOLUTION_CONFIRM_SECONDS = 10
GAME_MENU_BUTTON_LABELS = ["Emberstone", "Mobs", "Summon and Sacrifice"]
GAME_WINDOW_EMBERSTONE = "emberstone"
GAME_WINDOW_MOBS = "mobs"
GAME_WINDOW_SUMMON_AND_SACRIFICE = "summon_and_sacrifice"

class GameState:
    def __init__(self, screen, current_resolution, debug_enabled=False, tic_system=None):
        print("Initializing GameState...")

        self.screen = screen
        self.debug_enabled = debug_enabled
        self.tic_system = tic_system
        self.debug_framerate = 0
        self.image_manager = ImageManager.ImageManager()
        self.settings_open = False
        self.resolution_dropdown_open = False
        self.current_resolution = current_resolution
        self.fullscreen = False
        self.windowed_fullscreen = False
        self.pending_display_change = None
        self.settings_button_rect = pygame.Rect(0, 0, 0, 0)
        self.close_button_rect = pygame.Rect(0, 0, 0, 0)
        self.resolution_dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.resolution_option_rects = []
        self.windowed_fullscreen_checkbox_rect = pygame.Rect(0, 0, 0, 0)
        self.fullscreen_checkbox_rect = pygame.Rect(0, 0, 0, 0)
        self.confirm_resolution_open = False
        self.confirm_resolution_seconds = 0
        self.previous_display_settings = None
        self.confirm_yes_rect = pygame.Rect(0, 0, 0, 0)
        self.confirm_no_rect = pygame.Rect(0, 0, 0, 0)
        self.ignore_mouse_up_position = None
        self.active_game_window = GAME_WINDOW_EMBERSTONE
        self.game_menu_button_rects = []
        self.mob_cell_rects = []
        self.mob_pool_view_rect = pygame.Rect(0, 0, 0, 0)
        self.mob_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
        self.mob_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
        self.mob_pool_scroll_offset = 0
        self.mob_pool_scroll_max = 0
        self.dragging_mob_scrollbar = False
        self.mob_scrollbar_drag_offset = 0
        self.mouse_position = (-1, -1)
        self.selected_mob_index = 0
        self.infuse_button_rect = pygame.Rect(0, 0, 0, 0)
        self.summon_button_rect = pygame.Rect(0, 0, 0, 0)
        self.summon_rating_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.summon_rating_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.last_summoned_preview_rect = pygame.Rect(0, 0, 0, 0)
        self.summon_rating = 1
        self.emberstone_level = 1
        self.emberstone_lifeforce = 0
        self.debug_overlay_minimized = False
        self.debug_overlay_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_ember_core_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_lifeforce_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_stat_exp_button_rects = []
        self.essence_system = EssenceSystem()
        self.ember_core_system = EmberCoreSystem()
        self.mob_system = MobSystem()
        self.infuse_level = 0
        self.font = pygame.font.Font(FONTS / "PixelOperator8.ttf", 16)

    def set_debug_framerate(self, framerate):
        self.debug_framerate = framerate

    def handle_event(self, event):
        if hasattr(event, "pos"):
            self.mouse_position = event.pos

        if event.type == pygame.MOUSEWHEEL:
            if self.can_scroll_mob_pool():
                self.scroll_mob_pool(-event.y * MOB_SCROLL_WHEEL_PIXELS)
            return

        if event.type == pygame.MOUSEMOTION:
            if self.dragging_mob_scrollbar:
                self.drag_mob_scrollbar_to(event.pos[1])
            return

        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) or event.button != 1:
            return

        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_mob_scrollbar:
                self.dragging_mob_scrollbar = False
                return

            if self.ignore_mouse_up_position is not None:
                ignore_x, ignore_y = self.ignore_mouse_up_position
                event_x, event_y = event.pos
                self.ignore_mouse_up_position = None

                if abs(event_x - ignore_x) <= 2 and abs(event_y - ignore_y) <= 2:
                    return

            self.handle_click(event.pos)
            return

        if self.handle_mob_scrollbar_mouse_down(event.pos):
            return

        if self.handle_click(event.pos):
            self.ignore_mouse_up_position = event.pos

    def can_scroll_mob_pool(self):
        return (
            self.active_game_window == GAME_WINDOW_MOBS
            and not self.settings_open
            and not self.confirm_resolution_open
            and self.mob_pool_scroll_max > 0
            and (
                self.mob_pool_view_rect.collidepoint(self.mouse_position)
                or self.mob_scrollbar_track_rect.collidepoint(self.mouse_position)
            )
        )

    def handle_mob_scrollbar_mouse_down(self, position):
        if self.active_game_window != GAME_WINDOW_MOBS or self.mob_pool_scroll_max <= 0:
            return False

        if self.mob_scrollbar_thumb_rect.collidepoint(position):
            self.dragging_mob_scrollbar = True
            self.mob_scrollbar_drag_offset = position[1] - self.mob_scrollbar_thumb_rect.top
            return True

        if self.mob_scrollbar_track_rect.collidepoint(position):
            self.dragging_mob_scrollbar = True
            self.mob_scrollbar_drag_offset = self.mob_scrollbar_thumb_rect.height // 2
            self.drag_mob_scrollbar_to(position[1])
            return True

        return False

    def scroll_mob_pool(self, amount):
        self.set_mob_pool_scroll_offset(self.mob_pool_scroll_offset + amount)

    def set_mob_pool_scroll_offset(self, offset):
        self.mob_pool_scroll_offset = max(0, min(offset, self.mob_pool_scroll_max))

    def drag_mob_scrollbar_to(self, mouse_y):
        travel = self.mob_scrollbar_track_rect.height - self.mob_scrollbar_thumb_rect.height
        if travel <= 0:
            self.set_mob_pool_scroll_offset(0)
            return

        thumb_top = mouse_y - self.mob_scrollbar_drag_offset
        thumb_offset = thumb_top - self.mob_scrollbar_track_rect.top
        scroll_ratio = max(0, min(thumb_offset / travel, 1))
        self.set_mob_pool_scroll_offset(round(self.mob_pool_scroll_max * scroll_ratio))

    def handle_click(self, position):
        if self.confirm_resolution_open:
            if self.confirm_yes_rect.collidepoint(position):
                self.keep_pending_resolution()
            elif self.confirm_no_rect.collidepoint(position):
                self.revert_pending_resolution()
            return True

        if self.debug_enabled:
            if self.debug_overlay_toggle_rect.collidepoint(position):
                self.debug_overlay_minimized = not self.debug_overlay_minimized
                return True

            if not self.debug_overlay_minimized:
                if (
                    self.active_game_window == GAME_WINDOW_EMBERSTONE
                    and self.debug_ember_core_button_rect.collidepoint(position)
                ):
                    self.set_ember_cores_to_next_infuse_cost()
                    return True

                if (
                    self.active_game_window == GAME_WINDOW_EMBERSTONE
                    and self.debug_lifeforce_button_rect.collidepoint(position)
                ):
                    self.add_emberstone_lifeforce()
                    return True

                if self.active_game_window == GAME_WINDOW_MOBS:
                    for stat_name, rect in self.debug_stat_exp_button_rects:
                        if rect.collidepoint(position):
                            self.add_selected_mob_stat_experience(stat_name)
                            return True

        if self.settings_open:
            if self.settings_button_rect.collidepoint(position):
                self.settings_open = False
                self.resolution_dropdown_open = False
                return True

            if self.close_button_rect.collidepoint(position):
                self.settings_open = False
                self.resolution_dropdown_open = False
                return True

            if self.resolution_dropdown_open:
                for option, rect in self.resolution_option_rects:
                    if rect.collidepoint(position):
                        self.request_resolution_change(option)
                        self.resolution_dropdown_open = False
                        return True

                if self.fullscreen_checkbox_rect.collidepoint(position):
                    self.toggle_fullscreen()
                    return True

                if self.windowed_fullscreen_checkbox_rect.collidepoint(position):
                    self.toggle_windowed_fullscreen()
                    return True

                if self.resolution_dropdown_rect.collidepoint(position):
                    self.resolution_dropdown_open = False
                else:
                    self.resolution_dropdown_open = False
                return True

            if self.resolution_dropdown_rect.collidepoint(position):
                self.resolution_dropdown_open = True
                return True

            if self.fullscreen_checkbox_rect.collidepoint(position):
                self.toggle_fullscreen()
                return True

            if self.windowed_fullscreen_checkbox_rect.collidepoint(position):
                self.toggle_windowed_fullscreen()
                return True

            if not self.settings_rect().collidepoint(position):
                self.resolution_dropdown_open = False
            return True

        if self.settings_button_rect.collidepoint(position):
            self.settings_open = True
            return True

        for window_name, rect in self.game_menu_button_rects:
            if rect.collidepoint(position):
                self.active_game_window = window_name
                return True

        if self.active_game_window == GAME_WINDOW_MOBS:
            for mob_index, rect in self.mob_cell_rects:
                if rect.collidepoint(position):
                    self.selected_mob_index = mob_index
                    return True

        if self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE:
            if self.summon_rating_minus_rect.collidepoint(position):
                return self.decrease_summon_rating()

            if self.summon_rating_plus_rect.collidepoint(position):
                return self.increase_summon_rating()

            if self.last_summoned_preview_rect.collidepoint(position):
                return self.open_last_summoned_mob()

        if (
            self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE
            and self.summon_button_rect.collidepoint(position)
        ):
            return self.summon_mob()

        if (
            self.active_game_window == GAME_WINDOW_EMBERSTONE
            and self.infuse_button_rect.collidepoint(position)
        ):
            self.infuse_ember_cores()
            return True

        return False

    def consume_display_change(self):
        display_change = self.pending_display_change
        self.pending_display_change = None
        return display_change

    def update(self, dt, tics_elapsed=0, tics_per_second=1):
        self.essence_system.update_tics(tics_elapsed, tics_per_second)

        if self.confirm_resolution_open:
            self.confirm_resolution_seconds -= dt
            if self.confirm_resolution_seconds <= 0:
                self.revert_pending_resolution()

    def next_infuse_cost(self):
        return 2 ** self.infuse_level

    def infuse_ember_cores(self):
        if not self.ember_core_system.reduce_ember_cores(self.next_infuse_cost()):
            return False

        self.infuse_level += 1
        self.essence_system.multiply_essence_rate(2)
        return True

    def set_ember_cores_to_next_infuse_cost(self):
        target_amount = self.next_infuse_cost()
        current_amount = self.ember_core_system.get_ember_cores()

        if current_amount < target_amount:
            self.ember_core_system.increase_ember_cores(target_amount - current_amount)
        elif current_amount > target_amount:
            self.ember_core_system.reduce_ember_cores(current_amount - target_amount)

    def add_emberstone_lifeforce(self, amount=1):
        self.emberstone_lifeforce += amount

        while self.emberstone_lifeforce >= EMBERSTONE_LIFEFORCE_TO_LEVEL:
            self.emberstone_lifeforce -= EMBERSTONE_LIFEFORCE_TO_LEVEL
            self.emberstone_level += 1

    def emberstone_lifeforce_percentage(self):
        return self.emberstone_lifeforce * 100 / EMBERSTONE_LIFEFORCE_TO_LEVEL

    def increase_summon_rating(self):
        if self.summon_rating >= self.emberstone_level:
            return False

        self.summon_rating += 1
        return True

    def decrease_summon_rating(self):
        if self.summon_rating <= 1:
            return False

        self.summon_rating -= 1
        return True

    def summon_rating_text(self, rating):
        return "*" * rating

    def summon_cost(self):
        return BASE_SUMMON_COST * (10 ** (self.summon_rating - 1))

    def selected_mob(self):
        owned_mobs = self.mob_system.get_owned_mobs()
        if not owned_mobs:
            return None

        if self.selected_mob_index >= len(owned_mobs):
            self.selected_mob_index = 0

        return owned_mobs[self.selected_mob_index]

    def add_selected_mob_stat_experience(self, stat_name):
        if self.selected_mob() is None:
            return

        self.mob_system.add_stat_experience(self.selected_mob_index, stat_name)

    def can_afford_summon(self):
        return self.essence_system.has_essence(self.summon_cost())

    def summon_mob(self):
        if not self.essence_system.reduce_essence(self.summon_cost()):
            return False

        self.mob_system.summon_random_mob(self.summon_rating)
        self.selected_mob_index = len(self.mob_system.get_owned_mobs()) - 1
        return True

    def open_last_summoned_mob(self):
        last_summoned_mob = self.mob_system.get_last_summoned_mob()
        if last_summoned_mob is None:
            return False

        owned_mobs = self.mob_system.get_owned_mobs()
        last_summoned_index = self.owned_mob_identity_index(last_summoned_mob)
        if last_summoned_index is None:
            return False

        self.selected_mob_index = last_summoned_index
        self.active_game_window = GAME_WINDOW_MOBS
        self.scroll_to_mob_index(self.selected_mob_index)
        return True

    def owned_mob_identity_index(self, target_mob):
        for index, mob in enumerate(self.mob_system.get_owned_mobs()):
            if mob is target_mob:
                return index
        return None

    def scroll_to_mob_index(self, mob_index):
        columns, cell_size = self.mob_grid_dimensions(self.current_mob_pool_grid_width())
        visible_rows = max(1, math.ceil(self.current_mob_pool_grid_height() / cell_size))
        owned_rows = math.ceil(len(self.mob_system.get_owned_mobs()) / columns)
        rows = max(visible_rows, owned_rows)
        self.mob_pool_scroll_max = max(0, (rows * cell_size) - self.current_mob_pool_grid_height())
        target_row = mob_index // columns
        target_top = target_row * cell_size
        target_bottom = target_top + cell_size

        if target_top < self.mob_pool_scroll_offset:
            self.set_mob_pool_scroll_offset(target_top)
        elif target_bottom > self.mob_pool_scroll_offset + self.current_mob_pool_grid_height():
            self.set_mob_pool_scroll_offset(target_bottom - self.current_mob_pool_grid_height())

    def request_display_change(self):
        self.pending_display_change = (self.current_resolution, self.fullscreen, self.windowed_fullscreen)

    def request_resolution_change(self, resolution):
        if resolution == self.current_resolution:
            return

        self.previous_display_settings = (
            self.current_resolution,
            self.fullscreen,
            self.windowed_fullscreen,
        )
        self.current_resolution = resolution
        self.confirm_resolution_open = True
        self.confirm_resolution_seconds = RESOLUTION_CONFIRM_SECONDS
        self.request_display_change()

    def keep_pending_resolution(self):
        self.confirm_resolution_open = False
        self.previous_display_settings = None

    def revert_pending_resolution(self):
        if self.previous_display_settings is None:
            self.confirm_resolution_open = False
            return

        self.current_resolution, self.fullscreen, self.windowed_fullscreen = self.previous_display_settings
        self.confirm_resolution_open = False
        self.previous_display_settings = None
        self.request_display_change()

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)

    def set_fullscreen(self, fullscreen, request_display_change=True):
        self.fullscreen = fullscreen
        if fullscreen:
            self.windowed_fullscreen = False
        if request_display_change:
            self.request_display_change()

    def toggle_windowed_fullscreen(self):
        self.set_windowed_fullscreen(not self.windowed_fullscreen)

    def set_windowed_fullscreen(self, windowed_fullscreen, request_display_change=True):
        self.windowed_fullscreen = windowed_fullscreen
        if windowed_fullscreen:
            self.fullscreen = False
        if request_display_change:
            self.request_display_change()

    def set_display_modes(self, fullscreen, windowed_fullscreen, request_display_change=True):
        self.fullscreen = fullscreen
        self.windowed_fullscreen = windowed_fullscreen
        if self.fullscreen and self.windowed_fullscreen:
            self.windowed_fullscreen = False
        if request_display_change:
            self.request_display_change()

    def draw(self):
        self.draw_background()
        self.draw_settings_button()
        menu_rect = self.draw_game_menu()
        self.draw_active_game_window(menu_rect)

        if self.settings_open:
            self.draw_settings_window()

        if self.confirm_resolution_open:
            self.draw_resolution_confirmation_window()

        if self.debug_enabled:
            self.draw_debug_overlay()

    def draw_background(self):

        """screen stats"""
        width, height = self.screen.get_size()

        """draw main border"""
        # get tiles
        main_tiles = self.image_manager.get_border("main_border_png").get_tiles()
        self._draw_border(main_tiles, pygame.Rect(0, 0, width, height))

    def draw_settings_button(self):
        tile_size = ImageManager.TILE_SIZE
        self.settings_button_rect = self._draw_button("Settings", (tile_size, tile_size))

    def draw_game_menu(self):
        width, height = self.screen.get_size()
        top_gap = self.settings_button_rect.top
        menu_rect = pygame.Rect(
            self.settings_button_rect.left,
            self.settings_button_rect.bottom + top_gap,
            width // 4,
            height - self.settings_button_rect.bottom - (top_gap * 2),
        )

        inner_tiles = self.image_manager.get_border("inner_boarder_png").get_tiles()
        self._draw_border(inner_tiles, menu_rect)
        self.draw_game_menu_buttons(menu_rect)
        return menu_rect

    def draw_game_menu_buttons(self, menu_rect):
        tile_size = ImageManager.TILE_SIZE
        self.game_menu_button_rects = []
        button_rect = pygame.Rect(
            menu_rect.left + tile_size,
            menu_rect.top + tile_size,
            menu_rect.width - (tile_size * 2),
            MENU_BUTTON_HEIGHT,
        )

        window_names = [GAME_WINDOW_EMBERSTONE, GAME_WINDOW_MOBS, GAME_WINDOW_SUMMON_AND_SACRIFICE]
        for index, label in enumerate(GAME_MENU_BUTTON_LABELS):
            if button_rect.bottom > menu_rect.bottom - tile_size:
                return

            self._draw_button_in_rect(label, button_rect)
            self.game_menu_button_rects.append((window_names[index], button_rect.copy()))
            button_rect.y += MENU_BUTTON_HEIGHT + tile_size

        while button_rect.bottom <= menu_rect.bottom - tile_size:
            self._draw_button_in_rect("text", button_rect)
            button_rect.y += MENU_BUTTON_HEIGHT + tile_size

    def draw_active_game_window(self, menu_rect):
        window_rect = self.game_window_rect(menu_rect)
        inner_tiles = self.image_manager.get_border("inner_boarder_png").get_tiles()

        if self.active_game_window == GAME_WINDOW_MOBS:
            tile_size = ImageManager.TILE_SIZE
            left_width = int((window_rect.width - tile_size) * 0.7)
            right_width = window_rect.width - tile_size - left_width
            left_rect = pygame.Rect(window_rect.left, window_rect.top, left_width, window_rect.height)
            right_rect = pygame.Rect(left_rect.right + tile_size, window_rect.top, right_width, window_rect.height)
            self._draw_border(inner_tiles, left_rect)
            self._draw_border(inner_tiles, right_rect)
            self.draw_mobs_window(left_rect, right_rect)
            return

        if self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE:
            tile_size = ImageManager.TILE_SIZE
            left_width = (window_rect.width - tile_size) // 2
            right_width = window_rect.width - tile_size - left_width
            left_rect = pygame.Rect(window_rect.left, window_rect.top, left_width, window_rect.height)
            right_rect = pygame.Rect(left_rect.right + tile_size, window_rect.top, right_width, window_rect.height)
            self._draw_border(inner_tiles, left_rect)
            self._draw_border(inner_tiles, right_rect)
            self.draw_summon_window(left_rect)
            return

        self._draw_border(inner_tiles, window_rect)
        self.draw_emberstone_window(window_rect)

    def draw_mobs_window(self, left_rect, right_rect):
        self.draw_mob_pool(left_rect)
        self.draw_selected_mob_details(right_rect)

    def current_mob_pool_window_rect(self):
        menu_rect = self.current_game_menu_rect()
        window_rect = self.game_window_rect(menu_rect)
        tile_size = ImageManager.TILE_SIZE
        left_width = int((window_rect.width - tile_size) * 0.7)
        return pygame.Rect(window_rect.left, window_rect.top, left_width, window_rect.height)

    def current_game_menu_rect(self):
        width, height = self.screen.get_size()
        top_gap = self.settings_button_rect.top
        return pygame.Rect(
            self.settings_button_rect.left,
            self.settings_button_rect.bottom + top_gap,
            width // 4,
            height - self.settings_button_rect.bottom - (top_gap * 2),
        )

    def current_mob_pool_content_rect(self):
        return self.current_mob_pool_window_rect().inflate(
            -ImageManager.TILE_SIZE * 2,
            -ImageManager.TILE_SIZE * 2,
        )

    def current_mob_pool_grid_width(self):
        return self.current_mob_pool_content_rect().width

    def current_mob_pool_grid_height(self):
        return self.current_mob_pool_content_rect().height

    def draw_summon_window(self, window_rect):
        content_rect = window_rect.inflate(-ImageManager.TILE_SIZE * 2, -ImageManager.TILE_SIZE * 2)
        x = content_rect.left
        y = content_rect.top

        essence_text = self.font.render(self.essence_system.get_essence_text(), False, ESSENCE_TEXT_COLOR)
        essence_rect = essence_text.get_rect(midtop=(content_rect.centerx, y))
        self.screen.blit(essence_text, essence_rect)
        y = essence_rect.bottom + CONTROL_GAP

        self.summon_button_rect = self._draw_button("Summon", (x, y))
        cost_color = AFFORDABLE_TEXT_COLOR if self.can_afford_summon() else UNAFFORDABLE_TEXT_COLOR
        cost_text = self.font.render(
            "Cost: " + self.essence_system.format_number(self.summon_cost()),
            False,
            cost_color,
        )
        cost_rect = cost_text.get_rect(midleft=(self.summon_button_rect.right + 16, self.summon_button_rect.centery))
        self.screen.blit(cost_text, cost_rect)
        self.draw_summon_rating_controls(cost_rect)

        preview_top = self.summon_button_rect.bottom + ImageManager.TILE_SIZE * 2
        self.draw_last_summoned_mob_preview(content_rect, preview_top)

    def draw_summon_rating_controls(self, cost_rect):
        button_size = 24
        button_gap = 6
        self.summon_rating_plus_rect = pygame.Rect(
            cost_rect.right + 16,
            self.summon_button_rect.centery - button_size // 2,
            button_size,
            button_size,
        )
        self.summon_rating_minus_rect = pygame.Rect(
            self.summon_rating_plus_rect.right + button_gap,
            self.summon_rating_plus_rect.top,
            button_size,
            button_size,
        )

        plus_color = TEXT_COLOR if self.summon_rating < self.emberstone_level else GRID_LINE_COLOR
        minus_color = TEXT_COLOR if self.summon_rating > 1 else GRID_LINE_COLOR
        self._draw_button_in_rect("+", self.summon_rating_plus_rect, plus_color)
        self._draw_button_in_rect("-", self.summon_rating_minus_rect, minus_color)

        star_text = self.font.render(self.summon_rating_text(self.summon_rating), False, STAR_TEXT_COLOR)
        star_rect = star_text.get_rect(
            midleft=(self.summon_rating_minus_rect.right + 12, self.summon_rating_minus_rect.centery)
        )
        self.screen.blit(star_text, star_rect)

    def draw_last_summoned_mob_preview(self, content_rect, top):
        preview_cell = pygame.Rect(
            content_rect.left,
            top,
            SUMMON_PREVIEW_CELL_SIZE,
            SUMMON_PREVIEW_CELL_SIZE,
        )
        pygame.draw.rect(self.screen, GRID_LINE_COLOR, preview_cell, 1)
        self.last_summoned_preview_rect = pygame.Rect(0, 0, 0, 0)

        mob = self.mob_system.get_last_summoned_mob()
        if mob is None:
            self._draw_label("No summon yet", (preview_cell.right + 12, preview_cell.top), RATE_TEXT_COLOR)
            return

        self.last_summoned_preview_rect = preview_cell
        sprite = self.image_manager.get_mob(mob.sprite_key)
        sprite_rect = sprite.get_rect(center=preview_cell.center)
        self.screen.blit(sprite, sprite_rect)

        title_x = preview_cell.right + 12
        self._draw_label(mob.name, (title_x, preview_cell.top), ESSENCE_TEXT_COLOR)
        self._draw_label(self.summon_rating_text(mob.rating), (title_x, preview_cell.top + 20), STAR_TEXT_COLOR)
        self._draw_label(mob.mob_type, (title_x, preview_cell.top + 40), RATE_TEXT_COLOR)

        stats_top = preview_cell.bottom + ImageManager.TILE_SIZE
        column_width = content_rect.width // 2
        line_height = 18
        for index, stat_name in enumerate(MOB_STATS):
            column = index % 2
            row = index // 2
            stat_pos = (
                content_rect.left + (column * column_width),
                stats_top + (row * line_height),
            )
            self._draw_label(stat_name + ": " + str(mob.stats[stat_name]), stat_pos, ESSENCE_TEXT_COLOR)

    def draw_mob_pool(self, window_rect):
        content_rect = window_rect.inflate(-ImageManager.TILE_SIZE * 2, -ImageManager.TILE_SIZE * 2)
        self.mob_pool_view_rect = content_rect.copy()
        self.mob_scrollbar_track_rect = pygame.Rect(
            content_rect.right - MOB_SCROLLBAR_WIDTH,
            content_rect.top,
            MOB_SCROLLBAR_WIDTH,
            content_rect.height,
        )
        self.mob_cell_rects = []

        columns, cell_size = self.mob_grid_dimensions(self.mob_pool_view_rect.width)
        visible_rows = max(1, math.ceil(self.mob_pool_view_rect.height / cell_size))
        owned_mobs = self.mob_system.get_owned_mobs()
        owned_rows = math.ceil(len(owned_mobs) / columns) if owned_mobs else 0
        rows = max(visible_rows, owned_rows)
        content_height = rows * cell_size
        self.mob_pool_scroll_max = max(0, content_height - self.mob_pool_view_rect.height)
        self.set_mob_pool_scroll_offset(self.mob_pool_scroll_offset)

        previous_clip = self.screen.get_clip()
        self.screen.set_clip(self.mob_pool_view_rect)

        for row in range(rows):
            for column in range(columns):
                cell_index = (row * columns) + column
                cell_left = self.mob_pool_view_rect.left + (column * cell_size)
                cell_width = cell_size
                if column == columns - 1:
                    cell_width = self.mob_pool_view_rect.right - cell_left
                cell_rect = pygame.Rect(
                    cell_left,
                    self.mob_pool_view_rect.top + (row * cell_size) - self.mob_pool_scroll_offset,
                    cell_width,
                    cell_size,
                )
                if not cell_rect.colliderect(self.mob_pool_view_rect):
                    continue

                pygame.draw.rect(self.screen, GRID_LINE_COLOR, cell_rect, 1)

                if cell_index >= len(owned_mobs):
                    continue

                mob = owned_mobs[cell_index]
                sprite = self.image_manager.get_mob(mob.sprite_key)
                sprite_rect = sprite.get_rect(center=cell_rect.center)
                self.screen.blit(sprite, sprite_rect)
                self.mob_cell_rects.append((cell_index, cell_rect.clip(self.mob_pool_view_rect)))

        hovered_index = self.hovered_mob_index()
        if 0 <= self.selected_mob_index < len(owned_mobs):
            selected_rect = self.mob_cell_rect(self.selected_mob_index)
            if selected_rect is not None:
                pygame.draw.rect(self.screen, SELECTED_COLOR, selected_rect.inflate(-2, -2), 2)

        if hovered_index is not None and hovered_index != self.selected_mob_index:
            hover_rect = self.mob_cell_rect(hovered_index)
            if hover_rect is not None:
                pygame.draw.rect(self.screen, SELECTED_COLOR, hover_rect.inflate(-2, -2), 2)

        self.screen.set_clip(previous_clip)
        self.draw_mob_pool_scrollbar()

    def draw_mob_pool_scrollbar(self):
        pygame.draw.rect(self.screen, GRID_LINE_COLOR, self.mob_scrollbar_track_rect, 1)

        if self.mob_scrollbar_track_rect.height <= 0:
            self.mob_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
            return

        if self.mob_pool_scroll_max <= 0:
            self.mob_scrollbar_thumb_rect = self.mob_scrollbar_track_rect.copy()
        else:
            visible_ratio = self.mob_pool_view_rect.height / (self.mob_pool_view_rect.height + self.mob_pool_scroll_max)
            thumb_height = max(MOB_SCROLLBAR_MIN_THUMB_HEIGHT, int(self.mob_scrollbar_track_rect.height * visible_ratio))
            thumb_height = min(thumb_height, self.mob_scrollbar_track_rect.height)
            travel = self.mob_scrollbar_track_rect.height - thumb_height
            thumb_y = self.mob_scrollbar_track_rect.top
            if travel > 0:
                thumb_y += round(travel * self.mob_pool_scroll_offset / self.mob_pool_scroll_max)
            self.mob_scrollbar_thumb_rect = pygame.Rect(
                self.mob_scrollbar_track_rect.left,
                thumb_y,
                self.mob_scrollbar_track_rect.width,
                thumb_height,
            )

        pygame.draw.rect(self.screen, (150, 150, 150), self.mob_scrollbar_thumb_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.mob_scrollbar_thumb_rect, 1)

    def mob_grid_dimensions(self, content_width):
        max_columns = max(1, content_width // MOB_SPRITE_SIZE)
        for columns in range(max_columns, 1, -1):
            if content_width % columns == 0:
                return columns, content_width // columns

        if max_columns == 1:
            return 1, content_width

        return max_columns, content_width // max_columns

    def hovered_mob_index(self):
        for mob_index, rect in self.mob_cell_rects:
            if rect.collidepoint(self.mouse_position):
                return mob_index
        return None

    def mob_cell_rect(self, target_mob_index):
        for mob_index, rect in self.mob_cell_rects:
            if mob_index == target_mob_index:
                return rect
        return None

    def draw_selected_mob_details(self, window_rect):
        mob = self.selected_mob()
        if mob is None:
            return

        content_rect = window_rect.inflate(-ImageManager.TILE_SIZE * 2, -ImageManager.TILE_SIZE * 2)
        x = content_rect.left
        y = content_rect.top
        line_gap = 3

        sprite = self.image_manager.get_mob(mob.sprite_key)
        self.screen.blit(sprite, (x, y))

        title_x = x + MOB_SPRITE_SIZE + 12
        self._draw_label(mob.name, (title_x, y), ESSENCE_TEXT_COLOR)
        self._draw_label(self.summon_rating_text(mob.rating), (title_x, y + 18), STAR_TEXT_COLOR)
        self._draw_label(mob.mob_type, (title_x, y + 36), RATE_TEXT_COLOR)
        y += MOB_SPRITE_SIZE + 18

        for stat_name in MOB_STATS:
            value = mob.stats[stat_name]
            description = STAT_DESCRIPTIONS[stat_name]
            stat_text = stat_name + ": " + str(value)
            description_text = description

            self._draw_label(stat_text, (x, y), ESSENCE_TEXT_COLOR)
            y += 18
            self._draw_label(description_text, (x + 12, y), RATE_TEXT_COLOR)
            y += 17

            progress_rect = pygame.Rect(x, y, STAT_PROGRESS_BAR_SIZE[0], STAT_PROGRESS_BAR_SIZE[1])
            ProgressBar.draw_progress_bar(
                self.screen,
                self.image_manager,
                progress_rect,
                mob.get_stat_progress_percentage(stat_name),
            )
            y += STAT_PROGRESS_BAR_SIZE[1] + line_gap

    def _draw_label(self, text, position, color):
        label = self.font.render(text, False, color)
        self.screen.blit(label, position)

    def draw_emberstone_window(self, window_rect):
        emberstone_base = self.image_manager.get_object("emberstone_base_png")
        emberstone_rect = emberstone_base.get_rect(center=window_rect.center)
        self.draw_emberstone_lifeforce(emberstone_rect)
        self.screen.blit(emberstone_base, emberstone_rect)
        self.draw_emberstone_level(emberstone_rect)
        self.draw_emberstone_stats(emberstone_rect)
        self.draw_ember_core_controls(window_rect)

    def draw_emberstone_lifeforce(self, emberstone_rect):
        progress_rect = pygame.Rect(0, 0, STAT_PROGRESS_BAR_SIZE[0], STAT_PROGRESS_BAR_SIZE[1])
        progress_rect.midbottom = (emberstone_rect.centerx, emberstone_rect.top - 12)

        lifeforce_text = (
            "Lifeforce: "
            + str(self.emberstone_lifeforce)
            + "/"
            + str(EMBERSTONE_LIFEFORCE_TO_LEVEL)
        )
        lifeforce_label = self.font.render(lifeforce_text, False, LIFEFORCE_TEXT_COLOR)
        lifeforce_rect = lifeforce_label.get_rect(
            midbottom=(progress_rect.centerx, progress_rect.top - 4)
        )
        self.screen.blit(lifeforce_label, lifeforce_rect)

        ProgressBar.draw_progress_bar(
            self.screen,
            self.image_manager,
            progress_rect,
            self.emberstone_lifeforce_percentage(),
        )

    def draw_emberstone_level(self, emberstone_rect):
        level_text = self.font.render(str(self.emberstone_level), False, RATE_TEXT_COLOR)
        level_rect = level_text.get_rect(center=emberstone_rect.center)
        shadow_text = self.font.render(str(self.emberstone_level), False, TEXT_COLOR)
        for offset in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            self.screen.blit(shadow_text, level_rect.move(offset))
        self.screen.blit(level_text, level_rect)

    def draw_emberstone_stats(self, emberstone_rect):
        line_gap = 4
        top = emberstone_rect.bottom + ImageManager.TILE_SIZE

        essence_text = self.font.render(self.essence_system.get_essence_text(), False, ESSENCE_TEXT_COLOR)
        essence_rect = essence_text.get_rect(centerx=emberstone_rect.centerx, top=top)
        self.screen.blit(essence_text, essence_rect)

        rate_text = self.font.render(self.essence_system.get_rate_text(), False, RATE_TEXT_COLOR)
        rate_rect = rate_text.get_rect(centerx=emberstone_rect.centerx, top=essence_rect.bottom + line_gap)
        self.screen.blit(rate_text, rate_rect)

    def draw_ember_core_controls(self, window_rect):
        text_margin = ImageManager.TILE_SIZE * 2
        ember_core_text = self.font.render(
            "Ember Cores: " + str(self.ember_core_system.get_ember_cores()),
            False,
            ESSENCE_TEXT_COLOR,
        )
        ember_core_rect = ember_core_text.get_rect(
            topright=(window_rect.right - text_margin, window_rect.top + text_margin)
        )
        self.screen.blit(ember_core_text, ember_core_rect)

        self.infuse_button_rect = pygame.Rect(0, 0, 96, MENU_BUTTON_HEIGHT)
        self.infuse_button_rect.topright = (
            ember_core_rect.right,
            ember_core_rect.bottom + CONTROL_GAP,
        )
        self._draw_button_in_rect("Infuse", self.infuse_button_rect)

    def game_window_rect(self, menu_rect):
        width, height = self.screen.get_size()
        tile_gap = menu_rect.left
        return pygame.Rect(
            menu_rect.right + tile_gap,
            menu_rect.top,
            width - menu_rect.right - (tile_gap * 2),
            menu_rect.height,
        )

    def draw_settings_window(self):
        settings_rect = self.settings_rect()

        settings_tiles = self.image_manager.get_border("settings_border_png").get_tiles()
        self._draw_border(settings_tiles, settings_rect)

        close_button = self.image_manager.get_button("close_button_png")
        close_margin = 0
        self.close_button_rect = close_button.get_rect(
            topright=(settings_rect.right - close_margin, settings_rect.top + close_margin)
        )
        self.draw_settings_header(settings_rect)
        self.screen.blit(close_button, self.close_button_rect)
        self.draw_settings_options(settings_rect)

    def settings_rect(self):
        width, height = self.screen.get_size()
        settings_rect = pygame.Rect(0, 0, int(width * 0.8), int(height * 0.8))
        settings_rect.center = (width // 2, height // 2)
        return settings_rect

    def draw_settings_header(self, settings_rect):
        title = self.font.render("Settings", False, TEXT_COLOR)
        title_rect = title.get_rect(midleft=(settings_rect.left + 24, settings_rect.top + 32))
        self.screen.blit(title, title_rect)

    def draw_settings_options(self, settings_rect):
        self.draw_resolution_dropdown(settings_rect)
        self.draw_display_mode_checkboxes()

    def draw_resolution_dropdown(self, settings_rect):
        label = self.font.render("Resolution", False, TEXT_COLOR)
        label_pos = (
            settings_rect.left + SETTINGS_CONTENT_PADDING,
            settings_rect.top + SETTINGS_CONTENT_PADDING,
        )
        self.screen.blit(label, label_pos)

        self.resolution_dropdown_rect = pygame.Rect(
            label_pos[0],
            label_pos[1] + label.get_height() + CONTROL_GAP,
            DROPDOWN_WIDTH,
            DROPDOWN_HEIGHT,
        )
        self._draw_box(self.resolution_dropdown_rect, (180, 180, 180), TEXT_COLOR)
        self._draw_text(self.resolution_text(self.current_resolution), self.resolution_dropdown_rect, TEXT_COLOR)

        arrow_points = [
            (self.resolution_dropdown_rect.right - 22, self.resolution_dropdown_rect.centery - 4),
            (self.resolution_dropdown_rect.right - 10, self.resolution_dropdown_rect.centery - 4),
            (self.resolution_dropdown_rect.right - 16, self.resolution_dropdown_rect.centery + 5),
        ]
        pygame.draw.polygon(self.screen, TEXT_COLOR, arrow_points)

        self.resolution_option_rects = []
        if not self.resolution_dropdown_open:
            return

        for index, resolution in enumerate(RESOLUTION_OPTIONS):
            option_rect = pygame.Rect(
                self.resolution_dropdown_rect.left,
                self.resolution_dropdown_rect.bottom + (index * DROPDOWN_HEIGHT),
                DROPDOWN_WIDTH,
                DROPDOWN_HEIGHT,
            )
            fill_color = (205, 205, 205) if resolution == self.current_resolution else (190, 190, 190)
            self._draw_box(option_rect, fill_color, TEXT_COLOR)
            self._draw_text(self.resolution_text(resolution), option_rect, TEXT_COLOR)
            self.resolution_option_rects.append((resolution, option_rect))

    def draw_display_mode_checkboxes(self):
        checkbox_top = self.resolution_dropdown_rect.bottom + 28
        if self.resolution_dropdown_open and self.resolution_option_rects:
            checkbox_top = self.resolution_option_rects[-1][1].bottom + 20

        self.windowed_fullscreen_checkbox_rect = pygame.Rect(
            self.resolution_dropdown_rect.left,
            checkbox_top,
            CHECKBOX_SIZE,
            CHECKBOX_SIZE,
        )
        self._draw_checkbox(self.windowed_fullscreen_checkbox_rect, self.windowed_fullscreen)
        self._draw_checkbox_label("Windowed Fullscreen", self.windowed_fullscreen_checkbox_rect)

        self.fullscreen_checkbox_rect = pygame.Rect(
            self.resolution_dropdown_rect.left,
            self.windowed_fullscreen_checkbox_rect.bottom + 12,
            CHECKBOX_SIZE,
            CHECKBOX_SIZE,
        )
        self._draw_checkbox(self.fullscreen_checkbox_rect, self.fullscreen)
        self._draw_checkbox_label("Fullscreen", self.fullscreen_checkbox_rect)

    def draw_resolution_confirmation_window(self):
        width, height = self.screen.get_size()
        confirm_rect = pygame.Rect(0, 0, 520, 260)
        confirm_rect.center = (width // 2, height // 2)

        settings_tiles = self.image_manager.get_border("settings_border_png").get_tiles()
        self._draw_border(settings_tiles, confirm_rect)

        title = self.font.render("Keep this resolution?", False, TEXT_COLOR)
        title_rect = title.get_rect(center=(confirm_rect.centerx, confirm_rect.top + 64))
        self.screen.blit(title, title_rect)

        seconds = max(0, math.ceil(self.confirm_resolution_seconds))
        message = self.font.render("Reverting in " + str(seconds) + " seconds", False, TEXT_COLOR)
        message_rect = message.get_rect(center=(confirm_rect.centerx, confirm_rect.top + 112))
        self.screen.blit(message, message_rect)

        button_y = confirm_rect.top + 164
        self.confirm_yes_rect = self._draw_button("Yes", (confirm_rect.centerx - 132, button_y))
        self.confirm_no_rect = self._draw_button("No", (confirm_rect.centerx + 40, button_y))

    def draw_debug_overlay(self):
        self.debug_ember_core_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_lifeforce_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_stat_exp_button_rects = []

        if self.debug_overlay_minimized:
            self.draw_minimized_debug_overlay()
            return

        current_tic = 0
        if self.tic_system is not None:
            current_tic = self.tic_system.get_current_tic()

        lines = [
            "tic: " + str(current_tic),
            "fps: " + str(round(self.debug_framerate, 1)),
        ]
        rendered_lines = [self.font.render(line, False, (230, 230, 230)) for line in lines]
        emberstone_debug_button_labels = []
        if self.active_game_window == GAME_WINDOW_EMBERSTONE:
            emberstone_debug_button_labels = [
                "Set Cores: " + str(self.next_infuse_cost()),
                "Life +1",
            ]

        emberstone_debug_button_sizes = [self._button_size(label) for label in emberstone_debug_button_labels]
        emberstone_debug_button_width = max((size[0] for size in emberstone_debug_button_sizes), default=0)
        emberstone_debug_button_height = max((size[1] for size in emberstone_debug_button_sizes), default=0)
        emberstone_debug_buttons_height = 0
        if emberstone_debug_button_labels:
            emberstone_debug_buttons_height = (
                len(emberstone_debug_button_labels) * emberstone_debug_button_height
                + (len(emberstone_debug_button_labels) - 1) * CONTROL_GAP
            )

        stat_button_labels = []
        if self.active_game_window == GAME_WINDOW_MOBS and self.selected_mob() is not None:
            stat_button_labels = [(stat_name, stat_name[:2] + "+") for stat_name in MOB_STATS]

        stat_button_sizes = [self._button_size(label) for _, label in stat_button_labels]
        stat_columns = 5
        stat_button_gap = 4
        stat_button_rows = math.ceil(len(stat_button_labels) / stat_columns) if stat_button_labels else 0
        stat_button_width = max((size[0] for size in stat_button_sizes), default=0)
        stat_button_height = max((size[1] for size in stat_button_sizes), default=0)
        stat_buttons_width = 0
        stat_buttons_height = 0
        if stat_button_labels:
            visible_columns = min(stat_columns, len(stat_button_labels))
            stat_buttons_width = (visible_columns * stat_button_width) + ((visible_columns - 1) * stat_button_gap)
            stat_buttons_height = (stat_button_rows * stat_button_height) + ((stat_button_rows - 1) * stat_button_gap)

        padding = 6
        line_gap = 2
        text_width = max(line.get_width() for line in rendered_lines)
        text_height = sum(line.get_height() for line in rendered_lines) + line_gap
        overlay_width = max(
            text_width + DEBUG_TOGGLE_BUTTON_SIZE + padding,
            emberstone_debug_button_width,
            stat_buttons_width,
            DEBUG_TOGGLE_BUTTON_SIZE,
        ) + (padding * 2)
        overlay_height = text_height + (padding * 2)
        if emberstone_debug_button_labels:
            overlay_height += emberstone_debug_buttons_height + padding
        if stat_button_labels:
            overlay_height += stat_buttons_height + padding
        overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))

        overlay_pos = (self.screen.get_width() - overlay_width, 0)
        self.screen.blit(overlay, overlay_pos)
        self.debug_overlay_toggle_rect = pygame.Rect(
            overlay_pos[0] + overlay_width - DEBUG_TOGGLE_BUTTON_SIZE,
            overlay_pos[1],
            DEBUG_TOGGLE_BUTTON_SIZE,
            DEBUG_TOGGLE_BUTTON_SIZE,
        )
        self._draw_button_in_rect("-", self.debug_overlay_toggle_rect)

        y = padding
        for line in rendered_lines:
            self.screen.blit(line, (overlay_pos[0] + padding, overlay_pos[1] + y))
            y += line.get_height() + line_gap

        if emberstone_debug_button_labels:
            y += padding
            for index, label in enumerate(emberstone_debug_button_labels):
                button_rect = pygame.Rect(
                    overlay_pos[0] + padding,
                    overlay_pos[1] + y,
                    emberstone_debug_button_width,
                    emberstone_debug_button_height,
                )
                self._draw_button_in_rect(label, button_rect)
                if index == 0:
                    self.debug_ember_core_button_rect = button_rect
                else:
                    self.debug_lifeforce_button_rect = button_rect
                y += emberstone_debug_button_height + CONTROL_GAP

        if not stat_button_labels:
            return

        y += padding
        for index, (stat_name, label) in enumerate(stat_button_labels):
            column = index % stat_columns
            row = index // stat_columns
            button_rect = pygame.Rect(
                overlay_pos[0] + padding + (column * (stat_button_width + stat_button_gap)),
                overlay_pos[1] + y + (row * (stat_button_height + stat_button_gap)),
                stat_button_width,
                stat_button_height,
            )
            self._draw_button_in_rect(label, button_rect)
            self.debug_stat_exp_button_rects.append((stat_name, button_rect))

    def draw_minimized_debug_overlay(self):
        self.debug_overlay_toggle_rect = pygame.Rect(
            self.screen.get_width() - DEBUG_TOGGLE_BUTTON_SIZE,
            0,
            DEBUG_TOGGLE_BUTTON_SIZE,
            DEBUG_TOGGLE_BUTTON_SIZE,
        )
        self._draw_button_in_rect("+", self.debug_overlay_toggle_rect)

    def _draw_checkbox_label(self, text, checkbox_rect):
        label = self.font.render(text, False, TEXT_COLOR)
        label_rect = label.get_rect(midleft=(checkbox_rect.right + 8, checkbox_rect.centery))
        self.screen.blit(label, label_rect)

    @staticmethod
    def resolution_text(resolution):
        return str(resolution[0]) + " x " + str(resolution[1])

    def _draw_box(self, rect, fill_color, border_color):
        pygame.draw.rect(self.screen, fill_color, rect)
        pygame.draw.rect(self.screen, border_color, rect, 2)

    def _draw_text(self, text, rect, color):
        rendered_text = self.font.render(text, False, color)
        text_rect = rendered_text.get_rect(midleft=(rect.left + 8, rect.centery))
        self.screen.blit(rendered_text, text_rect)

    def _draw_checkbox(self, rect, checked):
        image_name = "checkbutton_checked_png" if checked else "checkbutton_unchecked_png"
        checkbox = pygame.transform.scale(self.image_manager.get_button(image_name), rect.size)
        self.screen.blit(checkbox, rect)

    def _draw_button(self, text, topleft):
        rendered_text = self.font.render(text, False, TEXT_COLOR)
        button_width, button_height = self._button_size(text, rendered_text)
        button_rect = pygame.Rect(topleft, (button_width, button_height))

        button_tiles = self.image_manager.get_button_base().get_tiles()
        self._draw_border(button_tiles, button_rect, BUTTON_TILE_SIZE)

        text_rect = rendered_text.get_rect(center=button_rect.center)
        self.screen.blit(rendered_text, text_rect)
        return button_rect

    def _button_size(self, text, rendered_text=None):
        if rendered_text is None:
            rendered_text = self.font.render(text, False, TEXT_COLOR)

        return (
            max(BUTTON_TILE_SIZE * 3, rendered_text.get_width() + (BUTTON_PADDING_X * 2)),
            max(BUTTON_TILE_SIZE * 3, rendered_text.get_height() + (BUTTON_PADDING_Y * 2)),
        )

    def _draw_button_in_rect(self, text, button_rect, text_color=TEXT_COLOR):
        rendered_text = self.font.render(text, False, text_color)
        button_tiles = self.image_manager.get_button_base().get_tiles()
        self._draw_border(button_tiles, button_rect, BUTTON_TILE_SIZE)

        text_rect = rendered_text.get_rect(center=button_rect.center)
        self.screen.blit(rendered_text, text_rect)
        return button_rect

    def _draw_border(self, tiles, area, tile_size=ImageManager.TILE_SIZE):

        self._tile_rect(
            tiles.center,
            pygame.Rect(
                area.left + tile_size,
                area.top + tile_size,
                area.width - (tile_size * 2),
                area.height - (tile_size * 2),
            ),
            tile_size,
        )

        self._tile_rect(
            tiles.top,
            pygame.Rect(area.left + tile_size, area.top, area.width - (tile_size * 2), tile_size),
            tile_size,
        )
        self._tile_rect(
            tiles.bottom,
            pygame.Rect(area.left + tile_size, area.bottom - tile_size, area.width - (tile_size * 2), tile_size),
            tile_size,
        )
        self._tile_rect(
            tiles.left,
            pygame.Rect(area.left, area.top + tile_size, tile_size, area.height - (tile_size * 2)),
            tile_size,
        )
        self._tile_rect(
            tiles.right,
            pygame.Rect(area.right - tile_size, area.top + tile_size, tile_size, area.height - (tile_size * 2)),
            tile_size,
        )

        self._blit_tile(tiles.top_left, area.topleft, tile_size)
        self._blit_tile(tiles.top_right, (area.right - tile_size, area.top), tile_size)
        self._blit_tile(tiles.bottom_left, (area.left, area.bottom - tile_size), tile_size)
        self._blit_tile(tiles.bottom_right, (area.right - tile_size, area.bottom - tile_size), tile_size)

    def _tile_rect(self, tile, area, tile_size=ImageManager.TILE_SIZE):
        if area.width <= 0 or area.height <= 0:
            return

        scaled_tile = self._scaled_tile(tile, tile_size)

        for y in range(area.top, area.bottom, tile_size):
            for x in range(area.left, area.right, tile_size):
                source = pygame.Rect(0, 0, min(tile_size, area.right - x), min(tile_size, area.bottom - y))
                self.screen.blit(scaled_tile, (x, y), source)

    def _blit_tile(self, tile, position, tile_size):
        self.screen.blit(self._scaled_tile(tile, tile_size), position)

    @staticmethod
    def _scaled_tile(tile, tile_size):
        if tile.get_size() == (tile_size, tile_size):
            return tile
        return pygame.transform.scale(tile, (tile_size, tile_size))
