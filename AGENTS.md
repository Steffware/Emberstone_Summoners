# AGENTS.md

Guidance for future agentic work in this repository.

## Project Snapshot

Emberstone Summoner is a small Python 3.10 pygame-ce project. The current game loop opens a `1600x900` window by default, draws into a fixed `1600x900` logical surface, smooth-scales that surface to the selected window resolution, and delegates input and drawing to `GameState`.

There is no package metadata, requirements file, or test suite at the moment. The existing virtual environment is `.venv/`.

## Repository Layout

- `src/config.py` - shared logical size, default resolution, and selectable 16:9 resolution options.
- `src/main.py` - pygame entry point. Initializes pygame, creates the resizable `pygame.Window` and logical game surface, maps mouse events into logical coordinates, imports `GameState`, and runs the 60 FPS loop. The game loop is wrapped in `main()` so helper functions can be imported safely.
- `src/TicSystem.py` - fixed-step tic system. It currently runs at two tics per second and returns how many tics elapsed on each frame update.
- `src/EssenceSystem.py` - tick-driven Essence resource system. Starts at `0` Essence with a `0.1/s` rate, exposes affordability/spend helpers, and formats numbers larger than `999` in compact exponential notation such as `1e3` and `1.234e3`.
- `src/EmberCoreSystem.py` - Ember Core resource system. Stores the player's Ember Core count and exposes increase, return, and reduce functions.
- `src/MobSystem.py` - Mob data and ownership system. Defines mob types, stat names/descriptions, base summon-pool mobs, per-stat experience/leveling, Adaptability XP multiplier behavior, random summoning, last-summoned tracking, and mob star ratings.
- `src/ProgressBar.py` - reusable progress bar renderer. Uses `assets/progressbar/progressbar_empty.png` as the track and tiles/clips `progressbar_fill.png` into the scaled fill area from a percentage.
- `src/GameState.py` - owns current game input and drawing. It draws the main background border, top-left Settings button, left game menu, Emberstone/Mobs/Summon and Sacrifice windows, settings modal, resolution dropdown, fullscreen checkboxes, debug overlay, mob scrolling, summoning controls, and all current game UI interactions.
- `src/ImageManager.py` - loads border, button, object, mob, and progress bar PNGs. 9-slice PNGs are sliced into `16x16` tiles and stored by name.
- `src/paths.py` - centralizes project-relative asset paths.
- `assets/borders/main_border.png` - runtime border tileset. Current image is `48x48` RGBA, arranged as a 3x3 grid of `16x16` tiles.
- `assets/borders/settings_border.png` - runtime settings window border tileset. Current image is `48x48` RGBA, arranged as a 3x3 grid of `16x16` tiles.
- `assets/borders/inner_boarder.png` - runtime inner panel/menu border tileset. Current image is `48x48` RGBA, arranged as a 3x3 grid of `16x16` tiles. The filename uses `boarder`.
- `assets/borders/main_border.pxo` - source/editable pixel-art project file for the border asset.
- `assets/buttons/base_button.png` - runtime button tileset. Current image is `48x48` RGBA, arranged as a 3x3 grid of `16x16` tiles.
- `assets/buttons/checkbutton_unchecked.png` and `assets/buttons/checkbutton_checked.png` - fullscreen checkbox states.
- `assets/buttons/close_button.png` - settings window close button. Current image is `64x64` RGBA.
- `assets/fonts/PixelOperator8.ttf` - pixel font used for drawn UI text.
- `assets/objects/emberstone_base.png` - Emberstone object sprite, drawn centered in the Emberstone window.
- `assets/progressbar/progressbar_empty.png` - progress bar empty/track image. Current image is `144x24`.
- `assets/progressbar/progressbar_fill.png` - progress bar fill tile. Current image is `14x16` and is tiled horizontally by `ProgressBar`.
- `assets/mobs/canine/Canis Placeholderus.png` - canine mob sprite. Current image is `48x48`.
- `assets/mobs/serpent/Danger Noodle.png` - serpent mob sprite. Current image is `48x48`.
- `assets/mobs/arachnid/Skitterblob.png` - arachnid mob sprite. Current image is `48x48`.

## Local Commands

Use the project virtualenv when available:

```bash
.venv/bin/python --version
.venv/bin/python -m py_compile src/main.py src/GameState.py src/ImageManager.py src/paths.py src/config.py src/TicSystem.py src/EssenceSystem.py src/EmberCoreSystem.py src/MobSystem.py src/ProgressBar.py
.venv/bin/python src/main.py
.venv/bin/python src/main.py debug
```

Known environment:

- Python: `3.10.12`
- pygame-ce: `2.5.7`

Running `src/main.py` opens a pygame window and may require a desktop/display session. In headless environments, prefer syntax checks or configure SDL explicitly before attempting runtime checks.

## Important Implementation Notes

- `ImageManager.TILE_SIZE` is currently `16`. 9-slice assets must be exactly `48x48` pixels so they slice into 9 `16x16` blocks.
- `config.LOGICAL_SIZE` is currently `(1600, 900)`. Future gameplay and UI should draw to the logical `GameState.screen` surface. `main.py` is responsible for smooth-scaling that logical surface to the physical window resolution.
- Mouse events with positions are mapped from physical window coordinates through the current viewport into logical coordinates in `main.py` before reaching `GameState`.
- Display changes are requested by `GameState.consume_display_change()` and applied by `main.py` through the active `pygame.Window`.
- Run `.venv/bin/python src/main.py debug` to enable the top-right debug overlay. It displays current tic/framerate, has a `-` minimize button that collapses to a `+` restore button, and shows context-sensitive debug controls. In the Emberstone window it shows `Set Cores` and `Life +1`; in the Mobs window it shows stat XP buttons only when a mob is selected.
- Future game systems should use `TicSystem` for fixed-step logic instead of frame-rate dependent updates. The game currently ticks at `2` tics per second.
- Essence is updated from elapsed tics, not frame delta. At the current `0.1/s` rate and `2` tics per second, each tic adds `0.05` Essence.
- Essence can be spent via `EssenceSystem.reduce_essence(amount)`, which returns `False` if the amount cannot be paid. Use `EssenceSystem.format_number()` for UI number display; values larger than `999` are displayed as exponential text, for example `1000` -> `1e3`, `1234` -> `1.234e3`, and `10000` -> `1e4`.
- Resolution changes are provisional: choosing a new resolution applies it immediately, opens a centered confirmation window with a 10-second countdown, and stores the previous display tuple for rollback. `Yes` keeps the new resolution; `No` or timeout restores the previous resolution and display mode.
- Windowed mode uses a resizable `pygame.Window` so the normal window manager maximize/fullscreen titlebar control is available.
- `Fullscreen` uses `pygame.Window.set_fullscreen(desktop=True)`. `Windowed Fullscreen` uses the same maximize/restore path as the window manager titlebar button via `pygame.Window.maximize()`.
- In fullscreen or windowed-fullscreen mode, the selected resolution remains the game viewport size, that viewport is centered, and the remaining screen area is filled black. `WINDOWMAXIMIZED` and `WINDOWRESTORED` update `GameState.windowed_fullscreen` so the in-game checkbox reflects window-manager changes.
- Border and base-button drawing share the same 9-slice helper. Full-screen/window borders use the source `16x16` tile size; small text buttons can pass a smaller draw tile size, such as `8`, to render compact controls from the same `48x48` base button. Draw text buttons with the base button and `PixelOperator8.ttf`; do not use the legacy pre-rendered `settings_button.png`.
- The tile mapper uses the first row/column for top/left, the last row/column for bottom/right, and `[1][1]` for center fill.
- `ImageManager` loads image assets at module import time and calls `convert_alpha()`. That requires pygame video initialization and a display mode to be set first. `main.py` currently handles this by creating `screen` before importing `GameState`.
- `GameState.draw()` fills the entire interior with the border center tile before drawing UI. Any future gameplay rendering will need a clear draw-order decision around this background fill.
- The left game menu is drawn with `inner_boarder.png`, aligned under the Settings button. It contains fixed-width base-button controls inset by one `ImageManager.TILE_SIZE` from the inner border, with one tile of vertical spacing.
- The first left-menu button is `Emberstone` and is active by default, drawing one right-side inner-border Emberstone window. The second is `Mobs`, drawing two right-side inner-border windows in the same overall area, split 70% left / 30% right with one tile gap between them. The third is `Summon and Sacrifice`, drawing two right-side inner-border windows spanning the same total area as the Emberstone window, split 50% / 50% with one tile gap.
- `ImageManager` also stores object sprites by name via `get_object()`. `emberstone_base_png` is currently drawn centered inside the Emberstone window.
- `ImageManager` stores mob sprites by `<folder>/<filename stem>` via `get_mob()`, for example `canine/Canis Placeholderus`, and progress bar assets via `get_progressbar()`.
- The Emberstone window draws the Emberstone sprite centered in the window. Above it are a red `Lifeforce: x/10` label and reusable progress bar. The Emberstone starts at level `1`; the level is drawn in blue over the sprite. Every 10 Lifeforce increases the Emberstone level by 1 and resets Lifeforce progress to 0.
- The Emberstone window still displays Essence and Essence rate below the sprite, and Ember Core controls in the top-right of the Emberstone window. `Infuse` costs `2 ** infuse_level`, consumes Ember Cores, increments `infuse_level`, and doubles Essence rate.
- Mobs are creatures owned by the player. The current mob stat list is `Vitality`, `Ferocity`, `Agility`, `Intuition`, `Precision`, `Brutality`, `Resilience`, `Arcane`, `Warding`, and `Adaptability`.
- `Vitality` represents Livepoints; `Ferocity` critical hit chance; `Agility` ticks until attack; `Intuition` evade chance; `Precision` hit chance; `Brutality` hit damage; `Resilience` damage reduction; `Arcane` magic damage; `Warding` magic reduction; `Adaptability` experience gain multiplier.
- The player starts with no owned mobs. `MobSystem.summon_pool` currently contains `Canis Placeholderus`, `Danger Noodle`, and `Skitterblob`; summoning creates a copy of a random pool mob and appends it to `owned_mobs`.
- One-star base mob stats, excluding Adaptability, each sum to 45. `Canis Placeholderus`: Vitality 5, Ferocity 10, Agility 5, Intuition 5, Precision 5, Brutality 10, Resilience 5, Arcane 0, Warding 0, Adaptability 1.0. `Danger Noodle`: Vitality 4, Ferocity 5, Agility 5, Intuition 10, Precision 5, Brutality 5, Resilience 3, Arcane 4, Warding 4, Adaptability 1.0. `Skitterblob`: Vitality 2, Ferocity 3, Agility 7, Intuition 5, Precision 10, Brutality 5, Resilience 3, Arcane 5, Warding 5, Adaptability 1.0.
- Mobs have a star rating. Base mobs are one star. The summon UI chooses a rating from 1 up to the current Emberstone level using `+` and `-` buttons, and renders the rating as gold `*` placeholders. Summon cost is `10 * (10 ** (rating - 1))`, so 1 star costs 10 Essence, 2 stars cost 100, and 3 stars cost `1e3`.
- The Summon and Sacrifice left window is the Summon window. It displays current Essence at the top, a `Summon` button below, a cost indicator to the right, `+` and `-` rating buttons, and gold star placeholders. The cost indicator is red when Essence is too low and green when the selected summon is affordable. Clicking `Summon` spends Essence, creates a random owned mob at the selected rating, stores it as the last summoned mob, and selects it in the Mobs screen.
- The Summon window shows the last summoned mob below the summon controls in a small cell with sprite, name, gold star rating, type, and stat values without progress bars. If no mob has been summoned yet it displays `No summon yet`.
- The Mobs left window shows the owned mob pool as a 7-column grid at the current logical resolution, with `48x48` sprites centered in each cell. The grid extends vertically beyond the visible area, is clipped to the window interior, scrolls with mouse wheel when hovered, and has a draggable right-edge scrollbar.
- Mobs can be selected from the pool. The selected cell has a white outline; hovering another visible mob draws a second white outline. The Mobs right window displays the selected mob sprite, name, gold star rating, type, stat descriptions, and per-stat progress bars.
- Each mob stat has independent experience. For now each stat needs 10 XP to level. XP gained is multiplied by the mob's current Adaptability before being applied. Non-Adaptability stats increase by 1 on level-up. Adaptability increases by 0.1 on level-up.
- The Mobs debug overlay stat buttons are abbreviated with the first two letters of the stat plus `+`, for example `Vi+` and `Fe+`. Each click gives 1 base XP to that stat on the selected mob, which is then multiplied by Adaptability.
- `ProgressBar.draw_progress_bar(screen, image_manager, rect, percentage)` is the reusable progress bar helper. It clamps `percentage` to `0..100`, scales the empty bar to `rect`, computes the fill inset from the `144x24` source dimensions, and tiles/clips the fill tile into the filled area.
- `GameState.handle_event()` currently owns mouse click handling for opening/closing settings, game-menu switching, summon controls, mob selection, debug buttons, and mob-pool wheel/scrollbar input.
- Asset paths should go through `src/paths.py` instead of relying on the process working directory.
- The import style is currently direct module imports from `src` (`import GameState`, `import ImageManager`, `from paths import BORDERS`) rather than package-relative imports.

## Development Preferences

- Keep changes small and consistent with the current simple module structure unless the task clearly calls for a broader architecture change.
- Avoid adding new frameworks or build systems without a concrete need.
- If adding assets, place them under `assets/` and add any new path constants to `src/paths.py`.
- If adding more image categories, follow the existing manager pattern but consider deferring image loading until after pygame display initialization is guaranteed.
- Prefer focused runtime smoke checks for pygame changes, plus `py_compile` for quick syntax validation.

## Current Gaps To Be Aware Of

- No automated tests are present.
- No dependency lockfile or installer metadata is present.
- Git commands currently do not behave as a normal repository in this environment, so do not assume `git status`, `git diff`, or other Git commands are available.
- `src/__pycache__/` exists locally and should not be treated as source.
