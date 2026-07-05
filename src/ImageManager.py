import pygame
from paths import BORDERS, BUTTONS, MOBS, OBJECTS, PROGRESSBARS

# config
ASSET_SCALE = 2
SOURCE_TILE_SIZE = 16
TILE_SIZE = SOURCE_TILE_SIZE * ASSET_SCALE


def load_scaled(path):
    png = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(
        png,
        (png.get_width() * ASSET_SCALE, png.get_height() * ASSET_SCALE),
    )

# raw images
raw_border_pngs = [
    ("main_border_png", load_scaled(BORDERS / "main_border.png")),
    ("settings_border_png", load_scaled(BORDERS / "settings_border.png")),
    ("inner_boarder_png", load_scaled(BORDERS / "inner_boarder.png")),
    ("mob_cell_png", load_scaled(BORDERS / "mob_cell.png")),
    ("mob_cell_highlited_png", load_scaled(BORDERS / "mob_cell_highlited.png")),
    ("mob_cell_sacrifice_png", load_scaled(BORDERS / "mob_cell_sacrifice.png")),
]
raw_button_pngs = [
    ("base_button_png", load_scaled(BUTTONS / "base_button.png")),
    ("base_button_highlighted_png", load_scaled(BUTTONS / "base_button_highlighted.png")),
    ("base_button_disabled_png", load_scaled(BUTTONS / "base_button_disabled.png")),
    ("checkbutton_unchecked_png", load_scaled(BUTTONS / "checkbutton_unchecked.png")),
    ("checkbutton_checked_png", load_scaled(BUTTONS / "checkbutton_checked.png")),
    ("close_button_png", load_scaled(BUTTONS / "close_button.png")),
    ("close_button_highlighted_png", load_scaled(BUTTONS / "close_button_highlighted.png")),
]
raw_object_pngs = [
    ("emberstone_base_png", load_scaled(OBJECTS / "emberstone_base.png")),
]
raw_progressbar_pngs = [
    ("progressbar_empty_png", load_scaled(PROGRESSBARS / "progressbar_empty.png")),
    ("progressbar_fill_png", load_scaled(PROGRESSBARS / "progressbar_fill.png")),
]


def load_mob_pngs():
    mob_pngs = []
    if not MOBS.exists():
        return mob_pngs

    for mob_type_dir in sorted(MOBS.iterdir()):
        if not mob_type_dir.is_dir():
            continue

        for mob_path in sorted(mob_type_dir.glob("*.png")):
            sprite_key = mob_type_dir.name + "/" + mob_path.stem
            mob_pngs.append((sprite_key, load_scaled(mob_path)))

    return mob_pngs


raw_mob_pngs = load_mob_pngs()

class Tiles:
    def __init__(self, tiles):
        self.top_left = tiles[0][0]
        self.top = tiles[0][1]
        self.top_right = tiles[0][-1]
        self.left = tiles[1][0]
        self.center = tiles[1][1]
        self.right = tiles[1][-1]
        self.bottom_left = tiles[-1][0]
        self.bottom = tiles[-1][1]
        self.bottom_right = tiles[-1][-1]

class Border:
    def __init__(self, name, raw_png):
        self.name = name
        self.tiles = Tiles(self.cut_tiles(raw_png))


    @staticmethod
    def cut_tiles(raw_png):
        expected_size = TILE_SIZE * 3
        if raw_png.get_width() != expected_size or raw_png.get_height() != expected_size:
            raise ValueError("Sliced images must be " + str(expected_size) + "x" + str(expected_size) + " pixels")

        tiles = []
        for y in range(0, raw_png.get_height(), TILE_SIZE):
            row = []
            for x in range(0, raw_png.get_width(), TILE_SIZE):
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                row.append(raw_png.subsurface(rect).copy())
            tiles.append(row)
        return tiles

    def get_name(self):
        return self.name

    def get_tiles(self):
        return self.tiles

class ImageManager:
    def __init__(self):
        self.borders = []
        self.buttons = {}
        self.objects = {}
        self.mobs = {}
        self.progressbars = {}
        self.button_base = None
        self.button_base_highlighted = None
        self.button_base_disabled = None

        for name, png in raw_border_pngs:
            self.borders.append(Border(name, png))

        for name, png in raw_button_pngs:
            if name == "base_button_png":
                self.button_base = Border(name, png)
            elif name == "base_button_highlighted_png":
                self.button_base_highlighted = Border(name, png)
            elif name == "base_button_disabled_png":
                self.button_base_disabled = Border(name, png)
            else:
                self.buttons[name] = png

        for name, png in raw_object_pngs:
            self.objects[name] = png

        for name, png in raw_progressbar_pngs:
            self.progressbars[name] = png

        for name, png in raw_mob_pngs:
            self.mobs[name] = png

    def add_border(self, image):
        self.borders.append(image)

    def get_border(self, name):
        for border in self.borders:
            if border.get_name() == name:
                return border
        raise KeyError("Border " + name + " not found")

    def get_button(self, name):
        try:
            return self.buttons[name]
        except KeyError:
            raise KeyError("Button " + name + " not found")

    def get_button_base(self):
        if self.button_base is None:
            raise KeyError("Button base not found")
        return self.button_base

    def get_button_base_highlighted(self):
        if self.button_base_highlighted is None:
            raise KeyError("Highlighted button base not found")
        return self.button_base_highlighted

    def get_button_base_disabled(self):
        if self.button_base_disabled is None:
            raise KeyError("Disabled button base not found")
        return self.button_base_disabled

    def get_object(self, name):
        try:
            return self.objects[name]
        except KeyError:
            raise KeyError("Object " + name + " not found")

    def get_mob(self, name):
        try:
            return self.mobs[name]
        except KeyError:
            raise KeyError("Mob " + name + " not found")

    def get_progressbar(self, name):
        try:
            return self.progressbars[name]
        except KeyError:
            raise KeyError("Progress bar " + name + " not found")
