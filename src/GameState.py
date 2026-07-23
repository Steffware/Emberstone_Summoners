import math
from EmberCoreSystem import EmberCoreSystem
from EssenceSystem import EssenceSystem
import ImageManager
import ProgressBar
from MobSystem import POTENTIAL_LEVELS, SPIRIT_TYPES, Mob, MobSystem
import pygame
from config import RESOLUTION_OPTIONS
from paths import FONTS

BUTTON_TILE_SIZE = 16
BUTTON_PADDING_X = 24
BUTTON_PADDING_Y = 8
SETTINGS_CONTENT_PADDING = 64
DROPDOWN_WIDTH = 160
DROPDOWN_HEIGHT = 56
CONTROL_GAP = 10
CHECKBOX_SIZE = 48
MENU_BUTTON_HEIGHT = 32
MOB_SPRITE_SIZE = 96
MOB_POOL_COLUMNS = 5
MOB_POOL_REFERENCE_COLUMNS = 7
EMBERSTONE_LIFEFORCE_TO_LEVEL = 100
BASE_SUMMON_COST = 10
SUMMON_PREVIEW_CELL_SIZE = 128
SACRIFICE_DROPDOWN_ROW_HEIGHT = 128
MOB_SCROLLBAR_WIDTH = 12
MOB_SCROLLBAR_MIN_THUMB_HEIGHT = 32
MOB_SCROLL_WHEEL_PIXELS = 160
POWER_PROGRESS_BAR_SIZE = (144, 24)
MOB_INFO_BORDER_PADDING = round(7.5 * ImageManager.ASSET_SCALE)
MOB_INFO_BODY_PADDING = round(MOB_INFO_BORDER_PADDING * 1.5)
DEBUG_TOGGLE_BUTTON_SIZE = 48
SACRIFICE_COOLDOWN_SECONDS = 60
TEXT_COLOR = (20, 20, 20)
ESSENCE_TEXT_COLOR = (245, 240, 220)
RATE_TEXT_COLOR = (90, 150, 210)
GRID_LINE_COLOR = (70, 64, 58)
SELECTED_COLOR = (255, 255, 255)
SCHEDULED_SACRIFICE_COLOR = (220, 40, 40)
LIFEFORCE_TEXT_COLOR = (220, 80, 80)
AFFORDABLE_TEXT_COLOR = (95, 220, 105)
UNAFFORDABLE_TEXT_COLOR = (220, 80, 80)
STAR_TEXT_COLOR = (245, 190, 65)
POTENTIAL_COLORS = {
    "Incompetent": (220, 40, 40),
    "Poor": (150, 150, 150),
    "Normal": (255, 255, 255),
    "Good": (95, 220, 105),
    "Exceptional": STAR_TEXT_COLOR,
}
SPIRIT_COLORS = {
    "Mundane": POTENTIAL_COLORS["Poor"],
    "Enchanted": POTENTIAL_COLORS["Normal"],
    "Arcane": (45, 85, 170),
    "Mystic": (205, 75, 255),
}
RESOLUTION_CONFIRM_SECONDS = 10
GAME_MENU_BUTTON_LABELS = ["Emberstone", "Mobs", "Summon and Sacrifice", "Adventure"]
GAME_WINDOW_EMBERSTONE = "emberstone"
GAME_WINDOW_MOBS = "mobs"
GAME_WINDOW_SUMMON_AND_SACRIFICE = "summon_and_sacrifice"
GAME_WINDOW_ADVENTURE = "adventure"

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
        self.sacrifice_dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_option_rects = []
        self.sacrifice_dropdown_open = False
        self.sacrifice_dropdown_list_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_dropdown_scroll_index = 0
        self.sacrifice_dropdown_scroll_max = 0
        self.sacrifice_dropdown_visible_count = 0
        self.sacrifice_dropdown_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_dropdown_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
        self.dragging_sacrifice_dropdown_scrollbar = False
        self.sacrifice_dropdown_scrollbar_drag_offset = 0
        self.selected_sacrifice_mob_index = None
        self.sacrifice_button_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_queue_button_rect = pygame.Rect(0, 0, 0, 0)
        self.auto_sacrifice_checkbox_rect = pygame.Rect(0, 0, 0, 0)
        self.auto_sacrifice_enabled = False
        self.sacrifice_queue = []
        self.sacrifice_queue_cell_rects = []
        self.sacrifice_queue_grid_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_queue_scroll_offset = 0
        self.sacrifice_queue_scroll_max = 0
        self.sacrifice_queue_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_queue_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
        self.dragging_sacrifice_queue_scrollbar = False
        self.sacrifice_queue_scrollbar_drag_offset = 0
        self.sacrifice_cooldown_seconds = 0
        self.emberstone_rect = pygame.Rect(0, 0, 0, 0)
        self.summon_rating = 1
        self.emberstone_level = 1
        self.emberstone_lifeforce = 0
        self.debug_overlay_minimized = False
        self.debug_overlay_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_ember_core_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_lifeforce_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_sacrifice_timer_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_power_exp_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spirit_exp_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_window_open = False
        self.debug_spawn_dropdown_open = False
        self.debug_spawn_selected_mob_index = 0
        self.debug_spawn_rating = 1
        self.debug_spawn_potential_dropdown_open = False
        self.debug_spawn_spirit_dropdown_open = False
        self.debug_spawn_selected_potential = "Normal"
        self.debug_spawn_selected_spirit = "Mundane"
        self.debug_spawn_dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_option_rects = []
        self.debug_spawn_rating_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_rating_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_potential_dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_potential_option_rects = []
        self.debug_spawn_spirit_dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_spirit_option_rects = []
        self.debug_spawn_confirm_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_close_button_rect = pygame.Rect(0, 0, 0, 0)
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

        if self.debug_spawn_window_open and self.handle_debug_spawn_keyboard_event(event):
            return

        if event.type == pygame.MOUSEWHEEL:
            if self.can_scroll_sacrifice_dropdown():
                self.scroll_sacrifice_dropdown(-event.y)
                return
            if self.can_scroll_sacrifice_queue():
                self.scroll_sacrifice_queue(-event.y * MOB_SCROLL_WHEEL_PIXELS)
                return
            if self.can_scroll_mob_pool():
                self.scroll_mob_pool(-event.y * MOB_SCROLL_WHEEL_PIXELS)
            return

        if event.type == pygame.MOUSEMOTION:
            if self.dragging_sacrifice_queue_scrollbar:
                self.drag_sacrifice_queue_scrollbar_to(event.pos[1])
                return
            if self.dragging_sacrifice_dropdown_scrollbar:
                self.drag_sacrifice_dropdown_scrollbar_to(event.pos[1])
                return
            if self.dragging_mob_scrollbar:
                self.drag_mob_scrollbar_to(event.pos[1])
            return

        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) or event.button != 1:
            return

        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_sacrifice_queue_scrollbar:
                self.dragging_sacrifice_queue_scrollbar = False
                return

            if self.dragging_sacrifice_dropdown_scrollbar:
                self.dragging_sacrifice_dropdown_scrollbar = False
                return

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

        if self.handle_sacrifice_dropdown_scrollbar_mouse_down(event.pos):
            return

        if self.handle_sacrifice_queue_scrollbar_mouse_down(event.pos):
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

    def can_scroll_sacrifice_dropdown(self):
        return (
            self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE
            and self.sacrifice_dropdown_open
            and not self.settings_open
            and not self.confirm_resolution_open
            and self.sacrifice_dropdown_scroll_max > 0
            and (
                self.sacrifice_dropdown_rect.collidepoint(self.mouse_position)
                or self.sacrifice_dropdown_list_rect.collidepoint(self.mouse_position)
                or self.sacrifice_dropdown_scrollbar_track_rect.collidepoint(self.mouse_position)
            )
        )

    def scroll_sacrifice_dropdown(self, amount):
        self.set_sacrifice_dropdown_scroll_index(self.sacrifice_dropdown_scroll_index + amount)

    def set_sacrifice_dropdown_scroll_index(self, index):
        self.sacrifice_dropdown_scroll_index = max(0, min(index, self.sacrifice_dropdown_scroll_max))

    def can_scroll_sacrifice_queue(self):
        return (
            self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE
            and not self.sacrifice_dropdown_open
            and not self.settings_open
            and not self.confirm_resolution_open
            and self.sacrifice_queue_scroll_max > 0
            and (
                self.sacrifice_queue_grid_rect.collidepoint(self.mouse_position)
                or self.sacrifice_queue_scrollbar_track_rect.collidepoint(self.mouse_position)
            )
        )

    def scroll_sacrifice_queue(self, amount):
        self.set_sacrifice_queue_scroll_offset(self.sacrifice_queue_scroll_offset + amount)

    def set_sacrifice_queue_scroll_offset(self, offset):
        self.sacrifice_queue_scroll_offset = max(0, min(offset, self.sacrifice_queue_scroll_max))

    def handle_sacrifice_queue_scrollbar_mouse_down(self, position):
        if (
            self.active_game_window != GAME_WINDOW_SUMMON_AND_SACRIFICE
            or self.sacrifice_dropdown_open
            or self.sacrifice_queue_scroll_max <= 0
        ):
            return False

        if self.sacrifice_queue_scrollbar_thumb_rect.collidepoint(position):
            self.dragging_sacrifice_queue_scrollbar = True
            self.sacrifice_queue_scrollbar_drag_offset = position[1] - self.sacrifice_queue_scrollbar_thumb_rect.top
            return True

        if self.sacrifice_queue_scrollbar_track_rect.collidepoint(position):
            self.dragging_sacrifice_queue_scrollbar = True
            self.sacrifice_queue_scrollbar_drag_offset = self.sacrifice_queue_scrollbar_thumb_rect.height // 2
            self.drag_sacrifice_queue_scrollbar_to(position[1])
            return True

        return False

    def drag_sacrifice_queue_scrollbar_to(self, mouse_y):
        travel = self.sacrifice_queue_scrollbar_track_rect.height - self.sacrifice_queue_scrollbar_thumb_rect.height
        if travel <= 0:
            self.set_sacrifice_queue_scroll_offset(0)
            return

        thumb_top = mouse_y - self.sacrifice_queue_scrollbar_drag_offset
        thumb_offset = thumb_top - self.sacrifice_queue_scrollbar_track_rect.top
        scroll_ratio = max(0, min(thumb_offset / travel, 1))
        self.set_sacrifice_queue_scroll_offset(round(self.sacrifice_queue_scroll_max * scroll_ratio))

    def handle_sacrifice_dropdown_scrollbar_mouse_down(self, position):
        if (
            self.active_game_window != GAME_WINDOW_SUMMON_AND_SACRIFICE
            or not self.sacrifice_dropdown_open
            or self.sacrifice_dropdown_scroll_max <= 0
        ):
            return False

        if self.sacrifice_dropdown_scrollbar_thumb_rect.collidepoint(position):
            self.dragging_sacrifice_dropdown_scrollbar = True
            self.sacrifice_dropdown_scrollbar_drag_offset = (
                position[1] - self.sacrifice_dropdown_scrollbar_thumb_rect.top
            )
            return True

        if self.sacrifice_dropdown_scrollbar_track_rect.collidepoint(position):
            self.dragging_sacrifice_dropdown_scrollbar = True
            self.sacrifice_dropdown_scrollbar_drag_offset = (
                self.sacrifice_dropdown_scrollbar_thumb_rect.height // 2
            )
            self.drag_sacrifice_dropdown_scrollbar_to(position[1])
            return True

        return False

    def drag_sacrifice_dropdown_scrollbar_to(self, mouse_y):
        travel = (
            self.sacrifice_dropdown_scrollbar_track_rect.height
            - self.sacrifice_dropdown_scrollbar_thumb_rect.height
        )
        if travel <= 0:
            self.set_sacrifice_dropdown_scroll_index(0)
            return

        thumb_top = mouse_y - self.sacrifice_dropdown_scrollbar_drag_offset
        thumb_offset = thumb_top - self.sacrifice_dropdown_scrollbar_track_rect.top
        scroll_ratio = max(0, min(thumb_offset / travel, 1))
        self.set_sacrifice_dropdown_scroll_index(round(self.sacrifice_dropdown_scroll_max * scroll_ratio))

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
        if self.debug_spawn_window_open:
            return self.handle_debug_spawn_click(position)

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

                if (
                    self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE
                    and self.debug_sacrifice_timer_button_rect.collidepoint(position)
                ):
                    self.reset_sacrifice_timer()
                    return True

                if (
                    self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE
                    and self.debug_spawn_button_rect.collidepoint(position)
                ):
                    self.open_debug_spawn_window()
                    return True

                if (
                    self.active_game_window == GAME_WINDOW_MOBS
                    and self.debug_power_exp_button_rect.collidepoint(position)
                ):
                    self.add_selected_mob_power_experience()
                    return True

                if (
                    self.active_game_window == GAME_WINDOW_MOBS
                    and self.debug_spirit_exp_button_rect.collidepoint(position)
                ):
                    self.add_selected_mob_spirit_experience()
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
            if self.sacrifice_dropdown_open:
                for mob_index, rect in self.sacrifice_option_rects:
                    if rect.collidepoint(position):
                        self.selected_sacrifice_mob_index = mob_index
                        self.sacrifice_dropdown_open = False
                        return True

                if not self.sacrifice_dropdown_rect.collidepoint(position):
                    self.sacrifice_dropdown_open = False
                    return True

            if self.sacrifice_dropdown_rect.collidepoint(position):
                self.sacrifice_dropdown_open = not self.sacrifice_dropdown_open
                return True

            for queue_index, rect in self.sacrifice_queue_cell_rects:
                if rect.collidepoint(position):
                    return self.select_queued_sacrifice_mob(queue_index)

            if self.sacrifice_button_rect.collidepoint(position):
                return self.sacrifice_selected_mob()

            if self.sacrifice_queue_button_rect.collidepoint(position):
                return self.toggle_selected_sacrifice_queue()

            if self.auto_sacrifice_checkbox_rect.collidepoint(position):
                self.toggle_auto_sacrifice()
                return True

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
            return self.infuse_ember_cores()

        if (
            self.active_game_window == GAME_WINDOW_EMBERSTONE
            and self.emberstone_rect.collidepoint(position)
        ):
            self.gain_emberstone_click_essence()
            return True

        return False

    def consume_display_change(self):
        display_change = self.pending_display_change
        self.pending_display_change = None
        return display_change

    def update(self, dt, tics_elapsed=0, tics_per_second=1):
        self.essence_system.update_tics(tics_elapsed, tics_per_second)
        self.update_sacrifice_cooldown(dt)
        self.process_auto_sacrifice_queue()

        if self.confirm_resolution_open:
            self.confirm_resolution_seconds -= dt
            if self.confirm_resolution_seconds <= 0:
                self.revert_pending_resolution()

    def update_sacrifice_cooldown(self, dt):
        if self.sacrifice_cooldown_seconds <= 0:
            return

        self.sacrifice_cooldown_seconds = max(0, self.sacrifice_cooldown_seconds - dt)

    def reset_sacrifice_timer(self):
        self.sacrifice_cooldown_seconds = 0
        self.process_auto_sacrifice_queue()

    def next_infuse_cost(self):
        return 2 ** self.infuse_level

    def infuse_ember_cores(self):
        if not self.ember_core_system.reduce_ember_cores(self.next_infuse_cost()):
            return False

        self.infuse_level += 1
        self.update_essence_rate()
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

        while self.emberstone_lifeforce >= self.next_emberstone_lifeforce_cost():
            self.emberstone_lifeforce -= self.next_emberstone_lifeforce_cost()
            self.emberstone_level += 1
            self.update_essence_rate()

    def next_emberstone_lifeforce_cost(self):
        return EMBERSTONE_LIFEFORCE_TO_LEVEL * (10 ** (self.emberstone_level - 1))

    def emberstone_lifeforce_percentage(self):
        return self.emberstone_lifeforce * 100 / self.next_emberstone_lifeforce_cost()

    def emberstone_lifeforce_text(self):
        return self.essence_system.format_number(self.emberstone_lifeforce)

    def update_essence_rate(self):
        self.essence_system.essence_rate = self.emberstone_level * 0.1 * (2 ** self.infuse_level)

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

    def add_selected_mob_power_experience(self):
        if self.selected_mob() is None:
            return

        self.mob_system.add_power_experience(self.selected_mob_index)

    def add_selected_mob_spirit_experience(self):
        if self.selected_mob() is None:
            return

        self.mob_system.add_spirit_experience(self.selected_mob_index)

    def can_afford_summon(self):
        return self.essence_system.has_essence(self.summon_cost())

    def summon_mob(self):
        if not self.essence_system.reduce_essence(self.summon_cost()):
            return False

        self.mob_system.summon_random_mob(self.summon_rating)
        self.selected_mob_index = len(self.mob_system.get_owned_mobs()) - 1
        return True

    def debug_spawn_selected_template(self):
        summon_pool = self.mob_system.summon_pool
        if not summon_pool:
            return None

        if self.debug_spawn_selected_mob_index >= len(summon_pool):
            self.debug_spawn_selected_mob_index = 0

        return summon_pool[self.debug_spawn_selected_mob_index]

    def open_debug_spawn_window(self):
        self.debug_spawn_window_open = True
        self.debug_spawn_dropdown_open = False
        self.debug_spawn_potential_dropdown_open = False
        self.debug_spawn_spirit_dropdown_open = False

    def close_debug_spawn_window(self):
        self.debug_spawn_window_open = False
        self.debug_spawn_dropdown_open = False
        self.debug_spawn_potential_dropdown_open = False
        self.debug_spawn_spirit_dropdown_open = False

    def handle_debug_spawn_keyboard_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close_debug_spawn_window()
            return True

        return False

    def handle_debug_spawn_click(self, position):
        if self.debug_spawn_close_button_rect.collidepoint(position):
            self.close_debug_spawn_window()
            return True

        if self.debug_spawn_dropdown_open:
            for mob_index, rect in self.debug_spawn_option_rects:
                if rect.collidepoint(position):
                    self.debug_spawn_selected_mob_index = mob_index
                    self.debug_spawn_dropdown_open = False
                    return True

            if not self.debug_spawn_dropdown_rect.collidepoint(position):
                self.debug_spawn_dropdown_open = False
                return True

        if self.debug_spawn_potential_dropdown_open:
            for potential, rect in self.debug_spawn_potential_option_rects:
                if rect.collidepoint(position):
                    self.debug_spawn_selected_potential = potential
                    self.debug_spawn_potential_dropdown_open = False
                    return True

            if not self.debug_spawn_potential_dropdown_rect.collidepoint(position):
                self.debug_spawn_potential_dropdown_open = False
                return True

        if self.debug_spawn_spirit_dropdown_open:
            for spirit_type, rect in self.debug_spawn_spirit_option_rects:
                if rect.collidepoint(position):
                    self.debug_spawn_selected_spirit = spirit_type
                    self.debug_spawn_spirit_dropdown_open = False
                    return True

            if not self.debug_spawn_spirit_dropdown_rect.collidepoint(position):
                self.debug_spawn_spirit_dropdown_open = False
                return True

        if self.debug_spawn_dropdown_rect.collidepoint(position):
            self.debug_spawn_dropdown_open = not self.debug_spawn_dropdown_open
            self.debug_spawn_potential_dropdown_open = False
            self.debug_spawn_spirit_dropdown_open = False
            return True

        if self.debug_spawn_potential_dropdown_rect.collidepoint(position):
            self.debug_spawn_potential_dropdown_open = not self.debug_spawn_potential_dropdown_open
            self.debug_spawn_dropdown_open = False
            self.debug_spawn_spirit_dropdown_open = False
            return True

        if self.debug_spawn_spirit_dropdown_rect.collidepoint(position):
            self.debug_spawn_spirit_dropdown_open = not self.debug_spawn_spirit_dropdown_open
            self.debug_spawn_dropdown_open = False
            self.debug_spawn_potential_dropdown_open = False
            return True

        if self.debug_spawn_rating_minus_rect.collidepoint(position):
            self.debug_spawn_rating = max(1, self.debug_spawn_rating - 1)
            return True

        if self.debug_spawn_rating_plus_rect.collidepoint(position):
            self.debug_spawn_rating = min(10, self.debug_spawn_rating + 1)
            return True

        if self.debug_spawn_confirm_button_rect.collidepoint(position):
            return self.spawn_debug_mob()

        return True

    def spawn_debug_mob(self):
        template = self.debug_spawn_selected_template()
        if template is None:
            return False

        spawned_mob = Mob(
            name=template.name,
            mob_type=template.mob_type,
            rating=self.debug_spawn_rating,
            potential=self.debug_spawn_selected_potential,
            spirit_type=self.debug_spawn_selected_spirit,
        )
        self.mob_system.add_owned_mob(spawned_mob)
        self.selected_mob_index = len(self.mob_system.get_owned_mobs()) - 1
        self.selected_sacrifice_mob_index = self.selected_mob_index
        return True

    def selected_sacrifice_mob(self):
        owned_mobs = self.mob_system.get_owned_mobs()
        if self.selected_sacrifice_mob_index is None:
            return None

        if self.selected_sacrifice_mob_index >= len(owned_mobs):
            self.selected_sacrifice_mob_index = None
            return None

        return owned_mobs[self.selected_sacrifice_mob_index]

    def mob_lifeforce_value(self, mob):
        return math.sqrt(mob.power)

    def mob_power_text(self, mob):
        return "Power: " + self.essence_system.format_number(mob.power)

    def draw_mob_power_line(self, mob, position, status_below=False):
        power_label = self._draw_outlined_label(self.mob_power_text(mob), position, LIFEFORCE_TEXT_COLOR)
        if not self.is_mob_queued_for_sacrifice(mob):
            return

        if status_below:
            status_position = (position[0], position[1] + power_label.get_height())
            status_text = "Being Sacrificed..."
        else:
            status_position = (position[0] + power_label.get_width(), position[1])
            status_text = " - Being Sacrificed..."
        self._draw_outlined_label(status_text, status_position, SCHEDULED_SACRIFICE_COLOR)

    def mob_power_experience_text(self, mob):
        current_experience = self.essence_system.format_number(mob.get_power_experience())
        next_level_experience = self.essence_system.format_number(mob.get_power_experience_to_level())
        return current_experience + "/" + next_level_experience

    def mob_spirit_experience_text(self, mob):
        current_experience = self.essence_system.format_number(mob.get_spirit_experience())
        next_level_experience = self.essence_system.format_number(mob.get_spirit_experience_to_level())
        return current_experience + "/" + next_level_experience

    def mob_potential_color(self, mob):
        return POTENTIAL_COLORS.get(mob.potential, POTENTIAL_COLORS["Normal"])

    def mob_potential_color_name(self, potential):
        return POTENTIAL_COLORS.get(potential, POTENTIAL_COLORS["Normal"])

    def mob_spirit_color(self, mob):
        return self.mob_spirit_color_name(mob.spirit_type)

    def mob_spirit_color_name(self, spirit_type):
        return SPIRIT_COLORS.get(spirit_type, SPIRIT_COLORS["Mundane"])

    def mob_potential_text(self, mob):
        return mob.potential + "(" + self.multiplier_text(mob.potential_multiplier()) + ")"

    def mob_spirit_text(self, mob):
        return "Spirit: " + mob.spirit_type + "(" + self.multiplier_text(mob.spirit_multiplier) + ")"

    def multiplier_text(self, multiplier):
        if float(multiplier).is_integer():
            return str(int(multiplier))
        return str(multiplier)

    def draw_mob_type(self, mob, position):
        self._draw_outlined_label(mob.mob_type, position, RATE_TEXT_COLOR)

    def draw_mob_potential_line(self, mob, position):
        prefix = "Potential: "
        prefix_label = self._draw_outlined_label(prefix, position, RATE_TEXT_COLOR)
        self._draw_outlined_label(
            self.mob_potential_text(mob),
            (position[0] + prefix_label.get_width(), position[1]),
            self.mob_potential_color(mob),
        )

    def draw_mob_spirit_line(self, mob, position):
        prefix = "Spirit: "
        prefix_label = self._draw_outlined_label(prefix, position, RATE_TEXT_COLOR)
        self._draw_outlined_label(
            mob.spirit_type + "(" + self.multiplier_text(mob.spirit_multiplier) + ")",
            (position[0] + prefix_label.get_width(), position[1]),
            self.mob_spirit_color(mob),
        )

    def can_sacrifice_selected_mob(self):
        return self.selected_sacrifice_mob() is not None and self.sacrifice_cooldown_seconds <= 0

    def sacrifice_selected_mob(self):
        if not self.can_sacrifice_selected_mob():
            return False

        mob = self.selected_sacrifice_mob()
        return self.sacrifice_mob(mob)

    def sacrifice_mob(self, mob):
        sacrificed_index = self.owned_mob_identity_index(mob)
        if sacrificed_index is None or self.sacrifice_cooldown_seconds > 0:
            return False

        self.add_emberstone_lifeforce(self.mob_lifeforce_value(mob))
        self.mob_system.remove_owned_mob(sacrificed_index)
        self.remove_mob_from_sacrifice_queue(mob)
        self.after_owned_mob_removed(sacrificed_index)
        self.sacrifice_cooldown_seconds = SACRIFICE_COOLDOWN_SECONDS
        return True

    def gain_emberstone_click_essence(self):
        self.essence_system.increase_essence(1)

    def can_toggle_selected_sacrifice_queue(self):
        return self.selected_sacrifice_mob() is not None

    def toggle_selected_sacrifice_queue(self):
        if not self.can_toggle_selected_sacrifice_queue():
            return False

        mob = self.selected_sacrifice_mob()
        if self.is_mob_queued_for_sacrifice(mob):
            self.remove_mob_from_sacrifice_queue(mob)
        else:
            self.sacrifice_queue.append(mob)
            self.process_auto_sacrifice_queue()
        return True

    def selected_sacrifice_queue_button_label(self):
        mob = self.selected_sacrifice_mob()
        if mob is not None and self.is_mob_queued_for_sacrifice(mob):
            return "Dequeue"
        return "Queue"

    def select_queued_sacrifice_mob(self, queue_index):
        self.sync_sacrifice_queue()
        if queue_index >= len(self.sacrifice_queue):
            return False

        owned_index = self.owned_mob_identity_index(self.sacrifice_queue[queue_index])
        if owned_index is None:
            return False

        self.selected_sacrifice_mob_index = owned_index
        return True

    def toggle_auto_sacrifice(self):
        self.auto_sacrifice_enabled = not self.auto_sacrifice_enabled
        self.process_auto_sacrifice_queue()

    def process_auto_sacrifice_queue(self):
        if not self.auto_sacrifice_enabled or self.sacrifice_cooldown_seconds > 0:
            return False

        mob = self.next_queued_sacrifice_mob()
        if mob is None:
            return False

        return self.sacrifice_mob(mob)

    def next_queued_sacrifice_mob(self):
        self.sync_sacrifice_queue()
        if not self.sacrifice_queue:
            return None
        return self.sacrifice_queue[0]

    def sync_sacrifice_queue(self):
        owned_ids = {id(mob) for mob in self.mob_system.get_owned_mobs()}
        self.sacrifice_queue = [mob for mob in self.sacrifice_queue if id(mob) in owned_ids]

    def remove_mob_from_sacrifice_queue(self, mob):
        self.sacrifice_queue = [queued_mob for queued_mob in self.sacrifice_queue if queued_mob is not mob]

    def is_mob_queued_for_sacrifice(self, mob):
        return any(queued_mob is mob for queued_mob in self.sacrifice_queue)

    def after_owned_mob_removed(self, removed_index):
        owned_count = len(self.mob_system.get_owned_mobs())

        if owned_count <= 0:
            self.selected_mob_index = 0
            self.selected_sacrifice_mob_index = None
            self.mob_pool_scroll_offset = 0
            self.mob_pool_scroll_max = 0
            return

        if self.selected_mob_index > removed_index:
            self.selected_mob_index -= 1
        elif self.selected_mob_index >= owned_count:
            self.selected_mob_index = owned_count - 1

        if self.selected_sacrifice_mob_index is not None:
            if self.selected_sacrifice_mob_index > removed_index:
                self.selected_sacrifice_mob_index -= 1
            elif self.selected_sacrifice_mob_index >= owned_count:
                self.selected_sacrifice_mob_index = owned_count - 1

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
        columns, cell_size = self.mob_pool_grid_dimensions(self.current_mob_pool_grid_width())
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
            if self.debug_spawn_window_open:
                self.draw_debug_spawn_window()

    def draw_background(self):

        """screen stats"""
        width, height = self.screen.get_size()

        """draw main border"""
        # get tiles
        main_tiles = self.image_manager.get_border("main_border_png").get_tiles()
        self._draw_border(main_tiles, pygame.Rect(0, 0, width, height))

    def draw_settings_button(self):
        button_height = self._button_size("Settings")[1]
        top_gap = button_height // 2
        self.settings_button_rect = self._draw_button("Settings", (ImageManager.TILE_SIZE, top_gap))

    def draw_game_menu(self):
        width, height = self.screen.get_size()
        top_gap = self.settings_button_rect.height // 2
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
        button_gap = tile_size // 2
        self.game_menu_button_rects = []
        button_rect = pygame.Rect(
            menu_rect.left + tile_size,
            menu_rect.top + tile_size,
            menu_rect.width - (tile_size * 2),
            MENU_BUTTON_HEIGHT,
        )

        window_names = [
            GAME_WINDOW_EMBERSTONE,
            GAME_WINDOW_MOBS,
            GAME_WINDOW_SUMMON_AND_SACRIFICE,
            GAME_WINDOW_ADVENTURE,
        ]
        for index, label in enumerate(GAME_MENU_BUTTON_LABELS):
            if button_rect.bottom > menu_rect.bottom - tile_size:
                return

            self._draw_button_in_rect(label, button_rect)
            self.game_menu_button_rects.append((window_names[index], button_rect.copy()))
            button_rect.y += MENU_BUTTON_HEIGHT + button_gap

        while button_rect.bottom <= menu_rect.bottom - tile_size:
            self._draw_button_in_rect("text", button_rect, disabled=True)
            button_rect.y += MENU_BUTTON_HEIGHT + button_gap

    def draw_active_game_window(self, menu_rect):
        window_rect = self.game_window_rect(menu_rect)
        inner_tiles = self.image_manager.get_border("inner_boarder_png").get_tiles()

        if self.active_game_window == GAME_WINDOW_MOBS:
            left_rect, right_rect = self.mob_window_rects(window_rect)
            self._draw_border(inner_tiles, left_rect)
            self._draw_border(inner_tiles, right_rect)
            self.draw_mobs_window(left_rect, right_rect)
            return

        if self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE:
            left_rect, right_rect = self.split_game_window_rects(window_rect)
            self._draw_border(inner_tiles, left_rect)
            self._draw_border(inner_tiles, right_rect)
            self.draw_summon_window(left_rect)
            self.draw_sacrifice_window(right_rect)
            return

        if self.active_game_window == GAME_WINDOW_ADVENTURE:
            left_rect, right_rect = self.split_game_window_rects(window_rect)
            self._draw_border(inner_tiles, left_rect)
            self._draw_border(inner_tiles, right_rect)
            return

        self._draw_border(inner_tiles, window_rect)
        self.draw_emberstone_window(window_rect)

    def draw_mobs_window(self, left_rect, right_rect):
        self.draw_mob_pool(left_rect)
        self.draw_selected_mob_details(right_rect)

    def split_game_window_rects(self, window_rect):
        tile_size = ImageManager.TILE_SIZE
        left_width = (window_rect.width - tile_size) // 2
        right_width = window_rect.width - tile_size - left_width
        left_rect = pygame.Rect(window_rect.left, window_rect.top, left_width, window_rect.height)
        right_rect = pygame.Rect(left_rect.right + tile_size, window_rect.top, right_width, window_rect.height)
        return left_rect, right_rect

    def mob_window_rects(self, window_rect):
        tile_size = ImageManager.TILE_SIZE
        available_width = window_rect.width - tile_size
        old_left_width = int(available_width * 0.7)
        old_content_width = max(0, old_left_width - (ImageManager.TILE_SIZE * 2))
        cell_size = max(MOB_SPRITE_SIZE, old_content_width // MOB_POOL_REFERENCE_COLUMNS)
        left_width = (cell_size * MOB_POOL_COLUMNS) + (ImageManager.TILE_SIZE * 2) + MOB_SCROLLBAR_WIDTH
        min_right_width = MOB_SPRITE_SIZE + (ImageManager.TILE_SIZE * 2)
        left_width = min(left_width, max(MOB_SPRITE_SIZE, available_width - min_right_width))
        right_width = available_width - left_width
        left_rect = pygame.Rect(window_rect.left, window_rect.top, left_width, window_rect.height)
        right_rect = pygame.Rect(left_rect.right + tile_size, window_rect.top, right_width, window_rect.height)
        return left_rect, right_rect

    def current_mob_pool_window_rect(self):
        menu_rect = self.current_game_menu_rect()
        window_rect = self.game_window_rect(menu_rect)
        left_rect, _ = self.mob_window_rects(window_rect)
        return left_rect

    def current_game_menu_rect(self):
        width, height = self.screen.get_size()
        top_gap = self.settings_button_rect.height // 2
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
        return max(0, self.current_mob_pool_content_rect().width - MOB_SCROLLBAR_WIDTH)

    def current_mob_pool_grid_height(self):
        return self.current_mob_pool_content_rect().height

    def draw_summon_window(self, window_rect):
        content_rect = window_rect.inflate(-ImageManager.TILE_SIZE * 2, -ImageManager.TILE_SIZE * 2)
        mob_info_rect = self.mob_info_content_rect(window_rect)
        x = content_rect.left
        y = content_rect.top

        essence_text = self.font.render(self.essence_system.get_essence_text(), False, ESSENCE_TEXT_COLOR)
        essence_rect = essence_text.get_rect(midtop=(content_rect.centerx, y))
        self.screen.blit(essence_text, essence_rect)
        y = essence_rect.bottom + CONTROL_GAP

        self.summon_button_rect = self._draw_button("Summon", (x, y), disabled=not self.can_afford_summon())
        cost_color = AFFORDABLE_TEXT_COLOR if self.can_afford_summon() else UNAFFORDABLE_TEXT_COLOR
        cost_text = self.font.render(
            "Cost: " + self.essence_system.format_number(self.summon_cost()),
            False,
            cost_color,
        )
        cost_rect = cost_text.get_rect(midleft=(self.summon_button_rect.right + 16, self.summon_button_rect.centery))
        self.screen.blit(cost_text, cost_rect)

        rating_bottom = self.draw_summon_rating_controls(
            content_rect.left,
            self.summon_button_rect.bottom + CONTROL_GAP,
        )
        preview_top = rating_bottom + CONTROL_GAP
        self.draw_last_summoned_mob_preview(mob_info_rect, preview_top)

    def draw_summon_rating_controls(self, left, top):
        button_size = self._button_size("+")
        button_gap = 6
        self.summon_rating_plus_rect = pygame.Rect(
            left,
            top,
            button_size[0],
            button_size[1],
        )
        self.summon_rating_minus_rect = pygame.Rect(
            self.summon_rating_plus_rect.right + button_gap,
            self.summon_rating_plus_rect.top,
            button_size[0],
            button_size[1],
        )

        self._draw_button_in_rect(
            "+",
            self.summon_rating_plus_rect,
            disabled=self.summon_rating >= self.emberstone_level,
        )
        self._draw_button_in_rect(
            "-",
            self.summon_rating_minus_rect,
            disabled=self.summon_rating <= 1,
        )

        star_text = self.font.render(self.summon_rating_text(self.summon_rating), False, STAR_TEXT_COLOR)
        star_rect = star_text.get_rect(
            midleft=(self.summon_rating_minus_rect.right + 12, self.summon_rating_minus_rect.centery)
        )
        self.screen.blit(star_text, star_rect)
        return max(self.summon_rating_minus_rect.bottom, star_rect.bottom)

    def draw_last_summoned_mob_preview(self, content_rect, top):
        preview_cell = pygame.Rect(
            content_rect.left,
            top,
            SUMMON_PREVIEW_CELL_SIZE,
            SUMMON_PREVIEW_CELL_SIZE,
        )
        self.last_summoned_preview_rect = pygame.Rect(0, 0, 0, 0)

        mob = self.mob_system.get_last_summoned_mob()
        if mob is None:
            self.draw_mob_cell_border(preview_cell)
            self._draw_label("No summon yet", (preview_cell.right + 12, preview_cell.top), RATE_TEXT_COLOR)
            return

        self.last_summoned_preview_rect = preview_cell
        self.draw_mob_detail_block(mob, preview_cell, content_rect.left, content_rect.right)

    def draw_sacrifice_window(self, window_rect):
        content_rect = window_rect.inflate(-ImageManager.TILE_SIZE * 2, -ImageManager.TILE_SIZE * 2)
        mob_info_rect = self.mob_info_content_rect(window_rect)
        self.sacrifice_button_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_queue_button_rect = pygame.Rect(0, 0, 0, 0)
        self.auto_sacrifice_checkbox_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_queue_cell_rects = []
        self.sacrifice_queue_grid_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_queue_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_queue_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
        self.sacrifice_dropdown_rect = pygame.Rect(
            content_rect.left,
            content_rect.top,
            content_rect.width,
            SACRIFICE_DROPDOWN_ROW_HEIGHT,
        )

        selected_mob = self.selected_sacrifice_mob()
        if selected_mob is None or self.sacrifice_dropdown_open:
            self.draw_sacrifice_dropdown(content_rect)
            if not self.sacrifice_dropdown_open:
                self.draw_sacrifice_queue(content_rect, self.sacrifice_dropdown_rect.bottom + ImageManager.TILE_SIZE)
            return

        preview_top = self.sacrifice_dropdown_rect.bottom + ImageManager.TILE_SIZE
        preview_bottom = self.draw_compact_mob_info(mob_info_rect, selected_mob, preview_top)
        button_top = preview_bottom + ImageManager.TILE_SIZE
        button_text = self.font.render("Sacrifice", False, TEXT_COLOR)
        button_size = self._button_size("Sacrifice", button_text)
        self.sacrifice_button_rect = pygame.Rect((content_rect.left, button_top), button_size)
        self._draw_button_in_rect(
            "Sacrifice",
            self.sacrifice_button_rect,
            disabled=not self.can_sacrifice_selected_mob(),
        )

        lifeforce_gain = self.mob_lifeforce_value(selected_mob)
        lifeforce_text = self.font.render(
            "Lifeforce: " + self.essence_system.format_number(lifeforce_gain),
            False,
            LIFEFORCE_TEXT_COLOR,
        )
        lifeforce_rect = lifeforce_text.get_rect(
            midleft=(self.sacrifice_button_rect.right + 16, self.sacrifice_button_rect.centery)
        )
        self.screen.blit(lifeforce_text, lifeforce_rect)

        if self.sacrifice_cooldown_seconds > 0:
            cooldown_text = self.font.render(
                "Cooldown: " + str(math.ceil(self.sacrifice_cooldown_seconds)) + "s",
                False,
                RATE_TEXT_COLOR,
            )
            cooldown_rect = cooldown_text.get_rect(
                topleft=(lifeforce_rect.left, lifeforce_rect.bottom + 4)
            )
            self.screen.blit(cooldown_text, cooldown_rect)

        queue_button_label = self.selected_sacrifice_queue_button_label()
        self.sacrifice_queue_button_rect = self._draw_button(
            queue_button_label,
            (content_rect.left, self.sacrifice_button_rect.bottom + CONTROL_GAP),
            disabled=not self.can_toggle_selected_sacrifice_queue(),
        )
        queue_top = self.sacrifice_queue_button_rect.bottom + ImageManager.TILE_SIZE
        self.draw_sacrifice_queue(content_rect, queue_top)
        self.draw_sacrifice_dropdown(content_rect)

    def draw_sacrifice_queue(self, content_rect, top):
        self.sync_sacrifice_queue()
        if top >= content_rect.bottom:
            self.sacrifice_queue_grid_rect = pygame.Rect(0, 0, 0, 0)
            self.sacrifice_queue_scroll_max = 0
            self.sacrifice_queue_scroll_offset = 0
            return

        self.auto_sacrifice_checkbox_rect = pygame.Rect(
            content_rect.left,
            top,
            CHECKBOX_SIZE,
            CHECKBOX_SIZE,
        )
        self._draw_checkbox(self.auto_sacrifice_checkbox_rect, self.auto_sacrifice_enabled)
        self._draw_checkbox_label("Auto Sacrifice", self.auto_sacrifice_checkbox_rect, ESSENCE_TEXT_COLOR)

        grid_top = self.auto_sacrifice_checkbox_rect.bottom + CONTROL_GAP
        queue_grid_rect = pygame.Rect(
            content_rect.left,
            grid_top,
            content_rect.width,
            max(0, content_rect.bottom - grid_top),
        )
        self.draw_sacrifice_queue_grid(queue_grid_rect)

    def draw_sacrifice_queue_grid(self, grid_rect):
        if grid_rect.width <= 0 or grid_rect.height <= 0:
            self.sacrifice_queue_grid_rect = pygame.Rect(0, 0, 0, 0)
            self.sacrifice_queue_scroll_max = 0
            self.sacrifice_queue_scroll_offset = 0
            return

        queue_count = len(self.sacrifice_queue)
        columns, cell_size = self.mob_grid_dimensions(grid_rect.width)
        rows = math.ceil(queue_count / columns) if queue_count else 0
        content_height = rows * cell_size
        self.sacrifice_queue_scroll_max = max(0, content_height - grid_rect.height)

        view_rect = grid_rect.copy()
        if self.sacrifice_queue_scroll_max > 0:
            view_rect.width = max(0, grid_rect.width - MOB_SCROLLBAR_WIDTH)
            columns, cell_size = self.mob_grid_dimensions(view_rect.width)
            rows = math.ceil(queue_count / columns) if queue_count else 0
            content_height = rows * cell_size
            self.sacrifice_queue_scroll_max = max(0, content_height - view_rect.height)
            self.sacrifice_queue_scrollbar_track_rect = pygame.Rect(
                grid_rect.right - MOB_SCROLLBAR_WIDTH,
                grid_rect.top,
                MOB_SCROLLBAR_WIDTH,
                grid_rect.height,
            )
        else:
            self.sacrifice_queue_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
            self.sacrifice_queue_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)

        self.sacrifice_queue_grid_rect = view_rect
        self.set_sacrifice_queue_scroll_offset(self.sacrifice_queue_scroll_offset)
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(view_rect)

        for queue_index, mob in enumerate(self.sacrifice_queue):
            row = queue_index // columns
            column = queue_index % columns
            cell_left = view_rect.left + (column * cell_size)
            cell_width = cell_size
            if column == columns - 1:
                cell_width = view_rect.right - cell_left

            cell_rect = pygame.Rect(
                cell_left,
                view_rect.top + (row * cell_size) - self.sacrifice_queue_scroll_offset,
                cell_width,
                cell_size,
            )
            if not cell_rect.colliderect(view_rect):
                continue

            self.draw_mob_cell_border(cell_rect, sacrifice=True)
            sprite = self.image_manager.get_mob(mob.sprite_key)
            sprite_rect = sprite.get_rect(center=cell_rect.center)
            self.screen.blit(sprite, sprite_rect)
            self.sacrifice_queue_cell_rects.append((queue_index, cell_rect.clip(view_rect)))

        self.screen.set_clip(previous_clip)
        self.draw_sacrifice_queue_scrollbar(content_height)

    def draw_sacrifice_queue_scrollbar(self, content_height):
        if self.sacrifice_queue_scroll_max <= 0:
            return

        pygame.draw.rect(self.screen, GRID_LINE_COLOR, self.sacrifice_queue_scrollbar_track_rect, 1)
        if self.sacrifice_queue_scrollbar_track_rect.height <= 0 or content_height <= 0:
            self.sacrifice_queue_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
            return

        visible_ratio = self.sacrifice_queue_grid_rect.height / content_height
        thumb_height = max(
            MOB_SCROLLBAR_MIN_THUMB_HEIGHT,
            int(self.sacrifice_queue_scrollbar_track_rect.height * visible_ratio),
        )
        thumb_height = min(thumb_height, self.sacrifice_queue_scrollbar_track_rect.height)
        travel = self.sacrifice_queue_scrollbar_track_rect.height - thumb_height
        thumb_y = self.sacrifice_queue_scrollbar_track_rect.top
        if travel > 0:
            thumb_y += round(travel * self.sacrifice_queue_scroll_offset / self.sacrifice_queue_scroll_max)

        self.sacrifice_queue_scrollbar_thumb_rect = pygame.Rect(
            self.sacrifice_queue_scrollbar_track_rect.left,
            thumb_y,
            self.sacrifice_queue_scrollbar_track_rect.width,
            thumb_height,
        )
        pygame.draw.rect(self.screen, (150, 150, 150), self.sacrifice_queue_scrollbar_thumb_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.sacrifice_queue_scrollbar_thumb_rect, 1)

    def draw_sacrifice_dropdown(self, content_rect):
        self.sacrifice_option_rects = []
        self.sacrifice_dropdown_rect = pygame.Rect(
            content_rect.left,
            content_rect.top,
            content_rect.width,
            SACRIFICE_DROPDOWN_ROW_HEIGHT,
        )
        self._draw_box(self.sacrifice_dropdown_rect, (10, 10, 10), GRID_LINE_COLOR)

        selected_mob = self.selected_sacrifice_mob()
        if selected_mob is None:
            self._draw_outlined_label(
                "Select Mob",
                (self.sacrifice_dropdown_rect.left + 12, self.sacrifice_dropdown_rect.top + 10),
                RATE_TEXT_COLOR,
            )
        else:
            sprite = self.image_manager.get_mob(selected_mob.sprite_key)
            sprite_rect = sprite.get_rect(
                midleft=(self.sacrifice_dropdown_rect.left + 12, self.sacrifice_dropdown_rect.centery)
            )
            self.screen.blit(sprite, sprite_rect)
            text_x = sprite_rect.right + 12
            self._draw_outlined_label(selected_mob.name, (text_x, self.sacrifice_dropdown_rect.top + 8), ESSENCE_TEXT_COLOR)
            self._draw_outlined_label(
                self.summon_rating_text(selected_mob.rating),
                (text_x, self.sacrifice_dropdown_rect.top + 28),
                STAR_TEXT_COLOR,
            )
            self.draw_mob_type(selected_mob, (text_x, self.sacrifice_dropdown_rect.top + 48))
            self.draw_mob_power_line(selected_mob, (text_x, self.sacrifice_dropdown_rect.top + 68), True)
            self.draw_scheduled_sacrifice_marker(selected_mob, self.sacrifice_dropdown_rect)

        arrow_points = [
            (self.sacrifice_dropdown_rect.right - 24, self.sacrifice_dropdown_rect.centery - 5),
            (self.sacrifice_dropdown_rect.right - 10, self.sacrifice_dropdown_rect.centery - 5),
            (self.sacrifice_dropdown_rect.right - 17, self.sacrifice_dropdown_rect.centery + 5),
        ]
        pygame.draw.polygon(self.screen, ESSENCE_TEXT_COLOR, arrow_points)

        if not self.sacrifice_dropdown_open:
            self.sacrifice_dropdown_list_rect = pygame.Rect(0, 0, 0, 0)
            self.sacrifice_dropdown_scroll_max = 0
            self.sacrifice_dropdown_scroll_index = 0
            self.sacrifice_dropdown_visible_count = 0
            self.sacrifice_dropdown_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
            self.sacrifice_dropdown_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
            return

        option_height = SACRIFICE_DROPDOWN_ROW_HEIGHT
        owned_mobs = self.mob_system.get_owned_mobs()
        visible_option_count = max(0, (content_rect.bottom - self.sacrifice_dropdown_rect.bottom) // option_height)
        self.sacrifice_dropdown_visible_count = visible_option_count
        self.sacrifice_dropdown_scroll_max = max(0, len(owned_mobs) - visible_option_count)
        self.set_sacrifice_dropdown_scroll_index(self.sacrifice_dropdown_scroll_index)
        list_height = visible_option_count * option_height
        self.sacrifice_dropdown_list_rect = pygame.Rect(
            self.sacrifice_dropdown_rect.left,
            self.sacrifice_dropdown_rect.bottom,
            self.sacrifice_dropdown_rect.width,
            list_height,
        )

        if visible_option_count <= 0:
            self.sacrifice_dropdown_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
            self.sacrifice_dropdown_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
            return

        option_width = self.sacrifice_dropdown_rect.width
        if self.sacrifice_dropdown_scroll_max > 0:
            self.sacrifice_dropdown_scrollbar_track_rect = pygame.Rect(
                self.sacrifice_dropdown_list_rect.right - MOB_SCROLLBAR_WIDTH,
                self.sacrifice_dropdown_list_rect.top,
                MOB_SCROLLBAR_WIDTH,
                self.sacrifice_dropdown_list_rect.height,
            )
            option_width -= MOB_SCROLLBAR_WIDTH
        else:
            self.sacrifice_dropdown_scrollbar_track_rect = pygame.Rect(0, 0, 0, 0)
            self.sacrifice_dropdown_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)

        previous_clip = self.screen.get_clip()
        self.screen.set_clip(self.sacrifice_dropdown_list_rect)

        first_mob_index = self.sacrifice_dropdown_scroll_index
        last_mob_index = min(len(owned_mobs), first_mob_index + visible_option_count)
        for visible_index, mob_index in enumerate(range(first_mob_index, last_mob_index)):
            mob = owned_mobs[mob_index]
            option_rect = pygame.Rect(
                self.sacrifice_dropdown_rect.left,
                self.sacrifice_dropdown_rect.bottom + (visible_index * option_height),
                option_width,
                option_height,
            )
            self._draw_box(option_rect, (20, 20, 20), GRID_LINE_COLOR)
            sprite = self.image_manager.get_mob(mob.sprite_key)
            sprite_rect = sprite.get_rect(midleft=(option_rect.left + 12, option_rect.centery))
            self.screen.blit(sprite, sprite_rect)
            text_x = sprite_rect.right + 12
            self._draw_outlined_label(mob.name, (text_x, option_rect.top + 8), ESSENCE_TEXT_COLOR)
            self._draw_outlined_label(
                self.summon_rating_text(mob.rating),
                (text_x, option_rect.top + 28),
                STAR_TEXT_COLOR,
            )
            self.draw_mob_type(mob, (text_x, option_rect.top + 48))
            self.draw_mob_power_line(mob, (text_x, option_rect.top + 68), True)
            self.draw_scheduled_sacrifice_marker(mob, option_rect)
            self.sacrifice_option_rects.append((mob_index, option_rect))

        self.screen.set_clip(previous_clip)
        self.draw_sacrifice_dropdown_scrollbar(len(owned_mobs))

    def draw_sacrifice_dropdown_scrollbar(self, owned_count):
        if self.sacrifice_dropdown_scroll_max <= 0:
            return

        pygame.draw.rect(self.screen, GRID_LINE_COLOR, self.sacrifice_dropdown_scrollbar_track_rect, 1)
        if self.sacrifice_dropdown_scrollbar_track_rect.height <= 0 or owned_count <= 0:
            self.sacrifice_dropdown_scrollbar_thumb_rect = pygame.Rect(0, 0, 0, 0)
            return

        visible_ratio = self.sacrifice_dropdown_visible_count / owned_count
        thumb_height = max(
            MOB_SCROLLBAR_MIN_THUMB_HEIGHT,
            int(self.sacrifice_dropdown_scrollbar_track_rect.height * visible_ratio),
        )
        thumb_height = min(thumb_height, self.sacrifice_dropdown_scrollbar_track_rect.height)
        travel = self.sacrifice_dropdown_scrollbar_track_rect.height - thumb_height
        thumb_y = self.sacrifice_dropdown_scrollbar_track_rect.top
        if travel > 0:
            thumb_y += round(travel * self.sacrifice_dropdown_scroll_index / self.sacrifice_dropdown_scroll_max)

        self.sacrifice_dropdown_scrollbar_thumb_rect = pygame.Rect(
            self.sacrifice_dropdown_scrollbar_track_rect.left,
            thumb_y,
            self.sacrifice_dropdown_scrollbar_track_rect.width,
            thumb_height,
        )
        pygame.draw.rect(self.screen, (150, 150, 150), self.sacrifice_dropdown_scrollbar_thumb_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.sacrifice_dropdown_scrollbar_thumb_rect, 1)

    def draw_scheduled_sacrifice_marker(self, mob, rect):
        if not self.is_mob_queued_for_sacrifice(mob):
            return

        pygame.draw.rect(self.screen, SCHEDULED_SACRIFICE_COLOR, rect.inflate(-2, -2), 2)

    def draw_compact_mob_info(self, content_rect, mob, top):
        header_rect = pygame.Rect(
            content_rect.left,
            top,
            content_rect.width,
            SUMMON_PREVIEW_CELL_SIZE + (MOB_INFO_BORDER_PADDING * 2),
        )
        self.draw_mob_info_border(header_rect)
        preview_cell = pygame.Rect(
            header_rect.left + MOB_INFO_BORDER_PADDING,
            header_rect.top + MOB_INFO_BORDER_PADDING,
            SUMMON_PREVIEW_CELL_SIZE,
            SUMMON_PREVIEW_CELL_SIZE,
        )
        self.draw_mob_cell_border(preview_cell, sacrifice=self.is_mob_queued_for_sacrifice(mob))

        sprite = self.image_manager.get_mob(mob.sprite_key)
        sprite_rect = sprite.get_rect(center=preview_cell.center)
        self.screen.blit(sprite, sprite_rect)

        title_x = preview_cell.right + MOB_INFO_BORDER_PADDING
        self._draw_outlined_label(mob.name, (title_x, preview_cell.top), ESSENCE_TEXT_COLOR)
        self._draw_outlined_label(self.summon_rating_text(mob.rating), (title_x, preview_cell.top + 20), STAR_TEXT_COLOR)
        self.draw_mob_type(mob, (title_x, preview_cell.top + 40))
        self.draw_mob_power_line(mob, (title_x, preview_cell.top + 60), True)

        return header_rect.bottom

    def draw_mob_pool(self, window_rect):
        content_rect = window_rect.inflate(-ImageManager.TILE_SIZE * 2, -ImageManager.TILE_SIZE * 2)
        self.mob_pool_view_rect = pygame.Rect(
            content_rect.left,
            content_rect.top,
            max(0, content_rect.width - MOB_SCROLLBAR_WIDTH),
            content_rect.height,
        )
        self.mob_scrollbar_track_rect = pygame.Rect(
            content_rect.right - MOB_SCROLLBAR_WIDTH,
            content_rect.top,
            MOB_SCROLLBAR_WIDTH,
            content_rect.height,
        )
        self.mob_cell_rects = []

        columns, cell_size = self.mob_pool_grid_dimensions(self.mob_pool_view_rect.width)
        visible_rows = max(1, math.ceil(self.mob_pool_view_rect.height / cell_size))
        owned_mobs = self.mob_system.get_owned_mobs()
        owned_rows = math.ceil(len(owned_mobs) / columns) if owned_mobs else 0
        rows = max(visible_rows, owned_rows)
        content_height = rows * cell_size
        self.mob_pool_scroll_max = max(0, content_height - self.mob_pool_view_rect.height)
        self.set_mob_pool_scroll_offset(self.mob_pool_scroll_offset)

        previous_clip = self.screen.get_clip()
        self.screen.set_clip(self.mob_pool_view_rect)
        hovered_index = self.hovered_mob_index()

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

                if cell_index >= len(owned_mobs):
                    continue

                mob = owned_mobs[cell_index]
                highlighted = cell_index == self.selected_mob_index or cell_index == hovered_index
                self.draw_mob_cell_border(
                    cell_rect,
                    highlighted,
                    self.is_mob_queued_for_sacrifice(mob),
                )
                sprite = self.image_manager.get_mob(mob.sprite_key)
                sprite_rect = sprite.get_rect(center=cell_rect.center)
                self.screen.blit(sprite, sprite_rect)
                self.mob_cell_rects.append((cell_index, cell_rect.clip(self.mob_pool_view_rect)))

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

    def mob_pool_grid_dimensions(self, content_width):
        columns = min(MOB_POOL_COLUMNS, max(1, content_width // MOB_SPRITE_SIZE))
        return columns, max(MOB_SPRITE_SIZE, content_width // columns)

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

        content_rect = self.mob_info_content_rect(window_rect)
        x = content_rect.left
        y = content_rect.top
        sprite_cell = pygame.Rect(x, y, MOB_SPRITE_SIZE, MOB_SPRITE_SIZE)
        self.draw_mob_detail_block(mob, sprite_cell, x, content_rect.right)

    def mob_info_content_rect(self, window_rect):
        return window_rect.inflate(-ImageManager.TILE_SIZE, -ImageManager.TILE_SIZE)

    def draw_mob_detail_block(self, mob, sprite_cell, details_x, right):
        line_height = self.font.get_height()
        line_step = round(line_height * 1.5)
        header_top = sprite_cell.top
        content_sprite_cell = sprite_cell.move(MOB_INFO_BORDER_PADDING, MOB_INFO_BORDER_PADDING)
        y = content_sprite_cell.top
        power_y = y + (line_step * 3)
        power_progress_top = power_y + line_height

        header_content_bottom = max(content_sprite_cell.bottom, power_progress_top + POWER_PROGRESS_BAR_SIZE[1])
        if self.is_mob_queued_for_sacrifice(mob):
            header_content_bottom += 4 + line_height
        header_bottom = header_content_bottom + MOB_INFO_BORDER_PADDING

        header_rect = pygame.Rect(
            sprite_cell.left,
            header_top,
            right - sprite_cell.left,
            header_bottom - header_top,
        )
        self.draw_mob_info_border(header_rect)

        self.draw_mob_cell_border(content_sprite_cell, sacrifice=self.is_mob_queued_for_sacrifice(mob))
        sprite = self.image_manager.get_mob(mob.sprite_key)
        sprite_rect = sprite.get_rect(center=content_sprite_cell.center)
        self.screen.blit(sprite, sprite_rect)

        title_x = content_sprite_cell.right + MOB_INFO_BORDER_PADDING
        self._draw_outlined_label(mob.name, (title_x, y), ESSENCE_TEXT_COLOR)
        self._draw_outlined_label(self.summon_rating_text(mob.rating), (title_x, y + line_step), STAR_TEXT_COLOR)
        self.draw_mob_type(mob, (title_x, y + (line_step * 2)))
        self._draw_outlined_label(self.mob_power_text(mob), (title_x, power_y), LIFEFORCE_TEXT_COLOR)

        progress_rect = self.draw_mob_detail_progress_bar(
            title_x,
            power_progress_top,
            mob.get_power_progress_percentage(),
            self.mob_power_experience_text(mob),
        )
        if self.is_mob_queued_for_sacrifice(mob):
            sacrifice_status_position = (title_x, progress_rect.bottom + 4)
            self._draw_outlined_label("Being Sacrificed...", sacrifice_status_position, SCHEDULED_SACRIFICE_COLOR)

        y = header_bottom + line_height
        spirit_y = y + (line_height * 2)
        spirit_progress_top = spirit_y + line_height
        body_bottom = spirit_progress_top + POWER_PROGRESS_BAR_SIZE[1]
        body_rect = pygame.Rect(
            details_x,
            y - MOB_INFO_BODY_PADDING,
            right - details_x,
            body_bottom - y + (MOB_INFO_BODY_PADDING * 2),
        )
        self.draw_mob_info_border(body_rect)

        body_content_x = details_x + MOB_INFO_BODY_PADDING
        y = body_rect.top + MOB_INFO_BODY_PADDING
        spirit_y = y + (line_height * 2)
        spirit_progress_top = spirit_y + line_height

        self.draw_mob_potential_line(mob, (body_content_x, y))
        self.draw_mob_spirit_line(mob, (body_content_x, spirit_y))

        self.draw_mob_detail_progress_bar(
            body_content_x,
            spirit_progress_top,
            mob.get_spirit_progress_percentage(),
            self.mob_spirit_experience_text(mob),
        )

    def draw_mob_info_border(self, rect):
        self._draw_border(self.image_manager.get_border("mob_info_border_png").get_tiles(), rect)

    def draw_mob_detail_progress_bar(self, left, top, percentage, experience_text):
        indent_label = self.font.render("┗", False, RATE_TEXT_COLOR)
        indent_rect = indent_label.get_rect(
            midleft=(left, top + (POWER_PROGRESS_BAR_SIZE[1] // 2))
        )
        self._draw_outlined_label("┗", indent_rect.topleft, RATE_TEXT_COLOR)

        progress_rect = pygame.Rect(
            indent_rect.right + 6,
            top,
            POWER_PROGRESS_BAR_SIZE[0],
            POWER_PROGRESS_BAR_SIZE[1],
        )
        ProgressBar.draw_progress_bar(
            self.screen,
            self.image_manager,
            progress_rect,
            percentage,
        )
        rendered_experience_text = self.font.render(experience_text, False, ESSENCE_TEXT_COLOR)
        experience_rect = rendered_experience_text.get_rect(
            midleft=(progress_rect.right + 8, progress_rect.centery)
        )
        self._draw_outlined_label(experience_text, experience_rect.topleft, ESSENCE_TEXT_COLOR)
        return progress_rect

    def _draw_label(self, text, position, color):
        label = self.font.render(text, False, color)
        self.screen.blit(label, position)
        return label

    def _draw_outlined_label(self, text, position, color, outline_color=(0, 0, 0)):
        label = self.font.render(text, False, color)
        outline = self.font.render(text, False, outline_color)
        x, y = position
        for offset_x, offset_y in (
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ):
            self.screen.blit(outline, (x + offset_x, y + offset_y))
        self.screen.blit(label, position)
        return label

    def draw_emberstone_window(self, window_rect):
        emberstone_base = self.image_manager.get_object("emberstone_base_png")
        emberstone_rect = emberstone_base.get_rect(center=window_rect.center)
        self.emberstone_rect = emberstone_rect.copy()
        self.draw_emberstone_lifeforce(emberstone_rect)
        self.screen.blit(emberstone_base, emberstone_rect)
        self.draw_emberstone_level(emberstone_rect)
        self.draw_emberstone_stats(emberstone_rect)
        self.draw_ember_core_controls(window_rect)

    def draw_emberstone_lifeforce(self, emberstone_rect):
        progress_rect = pygame.Rect(0, 0, POWER_PROGRESS_BAR_SIZE[0], POWER_PROGRESS_BAR_SIZE[1])
        progress_rect.midbottom = (emberstone_rect.centerx, emberstone_rect.top - 12)

        lifeforce_text = (
            "Lifeforce: "
            + self.emberstone_lifeforce_text()
            + "/"
            + self.essence_system.format_number(self.next_emberstone_lifeforce_cost())
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
        shadow_text = self.font.render(str(self.emberstone_level), False, TEXT_COLOR)
        level_text = pygame.transform.scale(
            level_text,
            (level_text.get_width() * 2, level_text.get_height() * 2),
        )
        shadow_text = pygame.transform.scale(
            shadow_text,
            (shadow_text.get_width() * 2, shadow_text.get_height() * 2),
        )
        level_rect = level_text.get_rect(center=emberstone_rect.center)
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
        text_margin = ImageManager.TILE_SIZE
        ember_core_text = self.font.render(
            "Ember Cores: " + str(self.ember_core_system.get_ember_cores()),
            False,
            ESSENCE_TEXT_COLOR,
        )
        ember_core_rect = ember_core_text.get_rect(
            topright=(window_rect.right - text_margin, window_rect.top + text_margin)
        )
        self.screen.blit(ember_core_text, ember_core_rect)

        self.infuse_button_rect = pygame.Rect(0, 0, 128, MENU_BUTTON_HEIGHT)
        self.infuse_button_rect.topright = (
            ember_core_rect.right,
            ember_core_rect.bottom + CONTROL_GAP,
        )
        self._draw_button_in_rect(
            "Infuse",
            self.infuse_button_rect,
            disabled=self.ember_core_system.get_ember_cores() < self.next_infuse_cost(),
        )

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
        if self.close_button_rect.collidepoint(self.mouse_position):
            close_button = self.image_manager.get_button("close_button_highlighted_png")
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

    def debug_spawn_window_rect(self):
        width, height = self.screen.get_size()
        window_rect = pygame.Rect(0, 0, 780, 360)
        window_rect.center = (width // 2, height // 2)
        return window_rect

    def draw_debug_spawn_window(self):
        window_rect = self.debug_spawn_window_rect()
        settings_tiles = self.image_manager.get_border("settings_border_png").get_tiles()
        self._draw_border(settings_tiles, window_rect)

        close_button = self.image_manager.get_button("close_button_png")
        self.debug_spawn_close_button_rect = close_button.get_rect(
            topright=(window_rect.right, window_rect.top)
        )
        if self.debug_spawn_close_button_rect.collidepoint(self.mouse_position):
            close_button = self.image_manager.get_button("close_button_highlighted_png")
        self.screen.blit(close_button, self.debug_spawn_close_button_rect)

        content_rect = window_rect.inflate(-SETTINGS_CONTENT_PADDING, -SETTINGS_CONTENT_PADDING)
        title = self.font.render("Debug Spawn", False, TEXT_COLOR)
        self.screen.blit(title, (content_rect.left, content_rect.top))

        y = content_rect.top + 42
        self.draw_debug_spawn_dropdown(content_rect.left, y, 360)
        self.draw_debug_spawn_rating_controls(content_rect.left + 390, y)
        self.draw_debug_spawn_potential_dropdown(content_rect.left, y + 76, 240)
        self.draw_debug_spawn_spirit_dropdown(content_rect.left + 270, y + 76, 220)

        template = self.debug_spawn_selected_template()
        if template is not None:
            sprite = self.image_manager.get_mob(template.sprite_key)
            sprite_rect = sprite.get_rect(topright=(content_rect.right, y))
            self.screen.blit(sprite, sprite_rect)

        self.debug_spawn_confirm_button_rect = self._draw_button(
            "Spawn",
            (content_rect.left, content_rect.bottom - MENU_BUTTON_HEIGHT - 8),
        )

        if self.debug_spawn_dropdown_open:
            self.draw_debug_spawn_dropdown_options()
        elif self.debug_spawn_potential_dropdown_open:
            self.draw_debug_spawn_potential_dropdown_options()
        elif self.debug_spawn_spirit_dropdown_open:
            self.draw_debug_spawn_spirit_dropdown_options()

    def draw_debug_spawn_dropdown(self, left, top, width):
        self.debug_spawn_dropdown_rect = pygame.Rect(left, top, width, DROPDOWN_HEIGHT)
        self._draw_box(self.debug_spawn_dropdown_rect, (180, 180, 180), TEXT_COLOR)

        template = self.debug_spawn_selected_template()
        label = "Select Mob"
        if template is not None:
            label = template.name + " (" + template.mob_type + ")"
        self._draw_dropdown_text(label, self.debug_spawn_dropdown_rect, TEXT_COLOR)

        arrow_points = [
            (self.debug_spawn_dropdown_rect.right - 22, self.debug_spawn_dropdown_rect.centery - 4),
            (self.debug_spawn_dropdown_rect.right - 10, self.debug_spawn_dropdown_rect.centery - 4),
            (self.debug_spawn_dropdown_rect.right - 16, self.debug_spawn_dropdown_rect.centery + 5),
        ]
        pygame.draw.polygon(self.screen, TEXT_COLOR, arrow_points)

    def draw_debug_spawn_potential_dropdown(self, left, top, width):
        self.debug_spawn_potential_dropdown_rect = pygame.Rect(left, top, width, DROPDOWN_HEIGHT)
        self.draw_debug_spawn_labeled_dropdown(
            self.debug_spawn_potential_dropdown_rect,
            "Potential: " + self.debug_spawn_selected_potential,
        )

    def draw_debug_spawn_spirit_dropdown(self, left, top, width):
        self.debug_spawn_spirit_dropdown_rect = pygame.Rect(left, top, width, DROPDOWN_HEIGHT)
        self.draw_debug_spawn_labeled_dropdown(
            self.debug_spawn_spirit_dropdown_rect,
            "Spirit: " + self.debug_spawn_selected_spirit,
        )

    def draw_debug_spawn_labeled_dropdown(self, rect, label):
        self._draw_box(rect, (180, 180, 180), TEXT_COLOR)
        self._draw_dropdown_text(label, rect, TEXT_COLOR)

        arrow_points = [
            (rect.right - 22, rect.centery - 4),
            (rect.right - 10, rect.centery - 4),
            (rect.right - 16, rect.centery + 5),
        ]
        pygame.draw.polygon(self.screen, TEXT_COLOR, arrow_points)

    def draw_debug_spawn_dropdown_options(self):
        self.debug_spawn_option_rects = []
        option_height = DROPDOWN_HEIGHT
        for mob_index, mob in enumerate(self.mob_system.summon_pool):
            option_rect = pygame.Rect(
                self.debug_spawn_dropdown_rect.left,
                self.debug_spawn_dropdown_rect.bottom + (mob_index * option_height),
                self.debug_spawn_dropdown_rect.width,
                option_height,
            )
            fill_color = (205, 205, 205) if mob_index == self.debug_spawn_selected_mob_index else (190, 190, 190)
            self._draw_box(option_rect, fill_color, TEXT_COLOR)
            self._draw_dropdown_text(mob.name + " (" + mob.mob_type + ")", option_rect, TEXT_COLOR)
            self.debug_spawn_option_rects.append((mob_index, option_rect))

    def draw_debug_spawn_potential_dropdown_options(self):
        self.debug_spawn_potential_option_rects = []
        option_height = DROPDOWN_HEIGHT
        for index, potential in enumerate(POTENTIAL_LEVELS):
            option_rect = pygame.Rect(
                self.debug_spawn_potential_dropdown_rect.left,
                self.debug_spawn_potential_dropdown_rect.bottom + (index * option_height),
                self.debug_spawn_potential_dropdown_rect.width,
                option_height,
            )
            fill_color = (205, 205, 205) if potential == self.debug_spawn_selected_potential else (190, 190, 190)
            self._draw_box(option_rect, fill_color, TEXT_COLOR)
            self._draw_dropdown_text(potential, option_rect, self.mob_potential_color_name(potential))
            self.debug_spawn_potential_option_rects.append((potential, option_rect))

    def draw_debug_spawn_spirit_dropdown_options(self):
        self.debug_spawn_spirit_option_rects = []
        option_height = DROPDOWN_HEIGHT
        for index, spirit_type in enumerate(SPIRIT_TYPES):
            option_rect = pygame.Rect(
                self.debug_spawn_spirit_dropdown_rect.left,
                self.debug_spawn_spirit_dropdown_rect.bottom + (index * option_height),
                self.debug_spawn_spirit_dropdown_rect.width,
                option_height,
            )
            fill_color = (205, 205, 205) if spirit_type == self.debug_spawn_selected_spirit else (190, 190, 190)
            self._draw_box(option_rect, fill_color, TEXT_COLOR)
            self._draw_dropdown_text(spirit_type, option_rect, self.mob_spirit_color_name(spirit_type))
            self.debug_spawn_spirit_option_rects.append((spirit_type, option_rect))

    def draw_debug_spawn_rating_controls(self, left, top):
        label = self.font.render("Stars:", False, TEXT_COLOR)
        self.screen.blit(label, (left, top + 5))

        button_size = 48
        self.debug_spawn_rating_minus_rect = pygame.Rect(left + 80, top, button_size, button_size)
        self.debug_spawn_rating_plus_rect = pygame.Rect(
            self.debug_spawn_rating_minus_rect.right + 8,
            top,
            button_size,
            button_size,
        )
        self._draw_button_in_rect("-", self.debug_spawn_rating_minus_rect, disabled=self.debug_spawn_rating <= 1)
        self._draw_button_in_rect("+", self.debug_spawn_rating_plus_rect, disabled=self.debug_spawn_rating >= 10)

        stars = self.font.render(self.summon_rating_text(self.debug_spawn_rating), False, STAR_TEXT_COLOR)
        self.screen.blit(stars, (self.debug_spawn_rating_plus_rect.right + 12, top + 5))

    def draw_debug_overlay(self):
        self.debug_ember_core_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_lifeforce_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_sacrifice_timer_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spawn_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_power_exp_button_rect = pygame.Rect(0, 0, 0, 0)
        self.debug_spirit_exp_button_rect = pygame.Rect(0, 0, 0, 0)

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
        debug_button_labels = []
        if self.active_game_window == GAME_WINDOW_EMBERSTONE:
            debug_button_labels = [
                "Set Cores: " + str(self.next_infuse_cost()),
                "Life +1",
            ]
        elif self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE:
            debug_button_labels = [
                "Reset Sac",
                "Spawn",
            ]
        elif self.active_game_window == GAME_WINDOW_MOBS and self.selected_mob() is not None:
            debug_button_labels = [
                "Power Exp +",
                "Spirit Exp +",
            ]

        debug_button_sizes = [self._button_size(label) for label in debug_button_labels]
        debug_button_width = max((size[0] for size in debug_button_sizes), default=0)
        debug_button_height = max((size[1] for size in debug_button_sizes), default=0)
        debug_buttons_height = 0
        if debug_button_labels:
            debug_buttons_height = (
                len(debug_button_labels) * debug_button_height
                + (len(debug_button_labels) - 1) * CONTROL_GAP
            )

        padding = 6
        line_gap = 2
        text_width = max(line.get_width() for line in rendered_lines)
        text_height = sum(line.get_height() for line in rendered_lines) + line_gap
        overlay_width = max(
            text_width + DEBUG_TOGGLE_BUTTON_SIZE + padding,
            debug_button_width,
            DEBUG_TOGGLE_BUTTON_SIZE,
        ) + (padding * 2)
        overlay_height = text_height + (padding * 2)
        if debug_button_labels:
            overlay_height += debug_buttons_height + padding
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

        if debug_button_labels:
            y += padding
            for index, label in enumerate(debug_button_labels):
                button_rect = pygame.Rect(
                    overlay_pos[0] + padding,
                    overlay_pos[1] + y,
                    debug_button_width,
                    debug_button_height,
                )
                self._draw_button_in_rect(label, button_rect)
                if self.active_game_window == GAME_WINDOW_EMBERSTONE and index == 0:
                    self.debug_ember_core_button_rect = button_rect
                elif self.active_game_window == GAME_WINDOW_EMBERSTONE and index == 1:
                    self.debug_lifeforce_button_rect = button_rect
                elif self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE and index == 0:
                    self.debug_sacrifice_timer_button_rect = button_rect
                elif self.active_game_window == GAME_WINDOW_SUMMON_AND_SACRIFICE and index == 1:
                    self.debug_spawn_button_rect = button_rect
                elif self.active_game_window == GAME_WINDOW_MOBS and index == 0:
                    self.debug_power_exp_button_rect = button_rect
                elif self.active_game_window == GAME_WINDOW_MOBS and index == 1:
                    self.debug_spirit_exp_button_rect = button_rect
                y += debug_button_height + CONTROL_GAP

    def draw_minimized_debug_overlay(self):
        self.debug_overlay_toggle_rect = pygame.Rect(
            self.screen.get_width() - DEBUG_TOGGLE_BUTTON_SIZE,
            0,
            DEBUG_TOGGLE_BUTTON_SIZE,
            DEBUG_TOGGLE_BUTTON_SIZE,
        )
        self._draw_button_in_rect("+", self.debug_overlay_toggle_rect)

    def _draw_checkbox_label(self, text, checkbox_rect, color=TEXT_COLOR):
        label = self.font.render(text, False, color)
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

    def _draw_dropdown_text(self, text, rect, color):
        text_rect = pygame.Rect(rect.left + 8, rect.top, rect.width - 38, rect.height)
        fitted_text = self._fit_text_to_width(text, text_rect.width)
        rendered_text = self.font.render(fitted_text, False, color)
        rendered_rect = rendered_text.get_rect(midleft=(text_rect.left, text_rect.centery))
        self.screen.blit(rendered_text, rendered_rect)

    def _fit_text_to_width(self, text, max_width):
        if self.font.size(text)[0] <= max_width:
            return text

        ellipsis = "..."
        ellipsis_width = self.font.size(ellipsis)[0]
        if ellipsis_width > max_width:
            return ""

        fitted_text = text
        while fitted_text and self.font.size(fitted_text)[0] + ellipsis_width > max_width:
            fitted_text = fitted_text[:-1]

        return fitted_text.rstrip() + ellipsis

    def _draw_checkbox(self, rect, checked):
        image_name = "checkbutton_checked_png" if checked else "checkbutton_unchecked_png"
        checkbox = pygame.transform.scale(self.image_manager.get_button(image_name), rect.size)
        self.screen.blit(checkbox, rect)

    def _draw_button(self, text, topleft, disabled=False):
        text_color = GRID_LINE_COLOR if disabled else TEXT_COLOR
        rendered_text = self.font.render(text, False, text_color)
        button_width, button_height = self._button_size(text, rendered_text)
        button_rect = pygame.Rect(topleft, (button_width, button_height))

        self._draw_button_frame(button_rect, disabled)

        text_rect = rendered_text.get_rect(center=button_rect.center)
        self.screen.blit(rendered_text, text_rect)
        return button_rect

    def _button_size(self, text, rendered_text=None):
        if rendered_text is None:
            rendered_text = self.font.render(text, False, TEXT_COLOR)

        return (
            max(BUTTON_TILE_SIZE * 2, rendered_text.get_width() + (BUTTON_PADDING_X * 2)),
            max(BUTTON_TILE_SIZE * 2, rendered_text.get_height() + (BUTTON_PADDING_Y * 2)),
        )

    def _draw_button_in_rect(self, text, button_rect, text_color=None, disabled=False):
        if text_color is None:
            text_color = GRID_LINE_COLOR if disabled else TEXT_COLOR

        rendered_text = self.font.render(text, False, text_color)
        self._draw_button_frame(button_rect, disabled)

        text_rect = rendered_text.get_rect(center=button_rect.center)
        self.screen.blit(rendered_text, text_rect)
        return button_rect

    def _draw_button_frame(self, button_rect, disabled=False):
        button_base = self.button_base_for_rect(button_rect, disabled)
        self._draw_border(button_base.get_tiles(), button_rect, BUTTON_TILE_SIZE)

    def button_base_for_rect(self, button_rect, disabled=False):
        if disabled:
            return self.image_manager.get_button_base_disabled()

        if button_rect.collidepoint(self.mouse_position):
            return self.image_manager.get_button_base_highlighted()

        return self.image_manager.get_button_base()

    def draw_mob_cell_border(self, rect, highlighted=False, sacrifice=False):
        if sacrifice:
            border_name = "mob_cell_sacrifice_png"
        elif highlighted:
            border_name = "mob_cell_highlited_png"
        else:
            border_name = "mob_cell_png"
        self._draw_border(self.image_manager.get_border(border_name).get_tiles(), rect)

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
