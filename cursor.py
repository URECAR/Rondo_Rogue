# cursor.py

import pygame
from properties import *
from support import SoundManager, InputManager
from database import CharacterDatabase, SOUND_PROPERTIES
from ui import ConfirmationDialog
import time # Import time for precise timing if needed, though pygame.time.get_ticks() is usually sufficient

class Cursor(pygame.sprite.Sprite):
    def __init__(self, pos, groups, level):
        super().__init__(groups)
        self.sprite_type = 'HPBar' # Should this be 'Cursor'?
        self.input_manager = InputManager()
        self.sound_manager = SoundManager()

        # Basic cursor attributes
        self.level = level
        self.level_data = level.level_data
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        start_pixel_x, start_pixel_y = pos[0] * TILESIZE, pos[1] * TILESIZE
        self.rect = self.image.get_rect(topleft=(start_pixel_x, start_pixel_y))
        self.collision_rect = self.rect.copy()
        self.pos = pygame.math.Vector2(pos[0], pos[1]) # Logical tile position
        self.previous_pos = self.pos.copy()

        # Control flags
        self.SW_select = False
        self.move_lock = False
        self.select_lock = False
        self.ismoving = False # General moving flag (for keyboard)
        self.clicked_self = False

        # Keyboard Movement variables
        self.move_cooldown = 300
        self.move_timer = 0
        self.move_per_tile = 20 # Keyboard move speed
        self.Goto = pygame.math.Vector2() # For keyboard movement offset
        self.held_key = None

        # Mouse Click/Drag (Timed Interpolation) variables
        self.is_click_moving = False # Flag for timed mouse move
        self.click_move_duration = 100 # milliseconds (0.3 seconds)
        self.click_move_start_time = 0
        self.click_move_start_pos = pygame.math.Vector2(self.rect.topleft) # Pixel start pos
        self.click_move_target_pos = pygame.math.Vector2(self.rect.topleft) # Pixel target pos

        # Drag specific variables
        self.is_dragging = False
        self.drag_start_pos_tile = None # Tile position where drag started
        self.last_drag_update_time = 0
        self.drag_update_interval = 50 # Update target every 50ms during drag

        # Display priority
        self.priority = self.level_data["Map_Max_y"]

        self.cached_image = None
        self.cached_selection_state = False

    def handle_input(self):
        current_time = pygame.time.get_ticks()

        # --- Block Input during timed move ---
        if self.is_click_moving:
            # Optionally handle cancel during timed move
            if self.input_manager.is_just_pressed('Cancel'):
                 self.is_click_moving = False # Stop the timed move
                 # Snap to current interpolation point or revert? Reverting might be jarring.
                 # Let's snap to where it currently is visually.
                 self.rect.topleft = (round(self.rect.x), round(self.rect.y))
                 self.collision_rect.topleft = self.rect.topleft
                 self.pos = pygame.math.Vector2(self.rect.x // TILESIZE, self.rect.y // TILESIZE)
                 self.previous_pos = self.pos.copy()
            return # Don't process other input while timed move is active

        # --- Keyboard Input (Only if not moving via keyboard OR mouse) ---
        direction_moves = {'Up': (0, -1), 'Left': (-1, 0), 'Down': (0, 1), 'Right': (1, 0)}
        if not self.move_lock and self.Goto.magnitude() == 0:
            # Key Held
            if self.held_key and current_time - self.move_timer >= self.move_cooldown:
                dx, dy = direction_moves[self.held_key]
                target_x_offset = dx * TILESIZE
                target_y_offset = dy * TILESIZE
                # Check map boundaries before setting Goto
                next_rect_x = self.rect.x + target_x_offset
                next_rect_y = self.rect.y + target_y_offset
                if 0 <= next_rect_x <= self.level_data["Map_Max_x"] - TILESIZE:
                     self.Goto.x = target_x_offset
                if 0 <= next_rect_y <= self.level_data["Map_Max_y"] - TILESIZE:
                    self.Goto.y = target_y_offset
                if self.Goto.magnitude() > 0:
                    self.move_timer = current_time # Reset timer only if a move is initiated
                    self.ismoving = True # Set keyboard moving flag

            # Key Just Pressed
            for direction in direction_moves:
                if self.input_manager.is_just_pressed(direction):
                    dx, dy = direction_moves[direction]
                    target_x_offset = dx * TILESIZE
                    target_y_offset = dy * TILESIZE
                    # Check map boundaries
                    next_rect_x = self.rect.x + target_x_offset
                    next_rect_y = self.rect.y + target_y_offset
                    temp_goto = pygame.math.Vector2()
                    if 0 <= next_rect_x <= self.level_data["Map_Max_x"] - TILESIZE:
                        temp_goto.x = target_x_offset
                    if 0 <= next_rect_y <= self.level_data["Map_Max_y"] - TILESIZE:
                        temp_goto.y = target_y_offset
                    if temp_goto.magnitude() > 0:
                         self.Goto = temp_goto
                         self.held_key = direction
                         self.move_timer = current_time
                         self.ismoving = True # Set keyboard moving flag
                         break

            # Key Released
            if self.held_key and self.input_manager.is_just_released(self.held_key):
                self.held_key = None

        # --- Mouse Input ---
        if not self.move_lock:
            mouse_pos_screen = self.input_manager.get_mouse_pos()
            world_x = mouse_pos_screen.x + self.level.visible_sprites.offset.x
            world_y = mouse_pos_screen.y + self.level.visible_sprites.offset.y
            tile_x = int(world_x // TILESIZE)
            tile_y = int(world_y // TILESIZE)
            target_pixel_x = tile_x * TILESIZE
            target_pixel_y = tile_y * TILESIZE

            # Clamp target pixel coordinates to map boundaries
            max_px = self.level_data["Map_Max_x"] - TILESIZE
            max_py = self.level_data["Map_Max_y"] - TILESIZE
            clamped_target_pixel_x = max(0, min(target_pixel_x, max_px))
            clamped_target_pixel_y = max(0, min(target_pixel_y, max_py))
            clamped_target_pos = pygame.math.Vector2(clamped_target_pixel_x, clamped_target_pixel_y)
            target_tile_valid = (0 <= tile_x < self.level_data["Map_Max_x"] // TILESIZE and
                                 0 <= tile_y < self.level_data["Map_Max_y"] // TILESIZE)


            # --- Dragging ---
            if self.input_manager.mouse_buttons[0]: # Left mouse button held
                if not self.is_dragging:
                    if target_tile_valid: # Start drag only on valid tiles
                        self.is_dragging = True
                        self.drag_start_pos_tile = pygame.math.Vector2(tile_x, tile_y)
                        self.last_drag_update_time = current_time
                        # Initiate the *first* move on drag start
                        if clamped_target_pos != self.rect.topleft:
                            self.click_move_start_pos = pygame.math.Vector2(self.rect.topleft)
                            self.click_move_target_pos = clamped_target_pos
                            self.click_move_start_time = current_time
                            self.is_click_moving = True
                            self.Goto = pygame.math.Vector2(0, 0) # Ensure keyboard move stops
                            self.ismoving = False

                elif self.is_dragging and target_tile_valid and (current_time - self.last_drag_update_time >= self.drag_update_interval):
                    # Update target position during drag frequently
                    if clamped_target_pos != self.click_move_target_pos: # Only update if target changed
                        self.click_move_start_pos = pygame.math.Vector2(self.rect.topleft) # Start from current pos
                        self.click_move_target_pos = clamped_target_pos
                        self.click_move_start_time = current_time # Restart timer
                        self.is_click_moving = True
                        self.Goto = pygame.math.Vector2(0, 0) # Ensure keyboard move stops
                        self.ismoving = False
                        self.last_drag_update_time = current_time
            else:
                # Stop dragging when button is released
                if self.is_dragging:
                    self.is_dragging = False
                    self.drag_start_pos_tile = None

            # --- Clicking (only if not dragging and not already keyboard moving) ---
            if (not self.is_dragging and self.input_manager.is_left_click() and self.Goto.magnitude() == 0):
                 if target_tile_valid:
                    current_tile_x = self.rect.x // TILESIZE
                    current_tile_y = self.rect.y // TILESIZE

                    if tile_x == current_tile_x and tile_y == current_tile_y:
                        self.clicked_self = True # Handle selection/confirmation
                    elif clamped_target_pos != self.rect.topleft:
                        # Initiate Timed Movement
                        self.click_move_start_pos = pygame.math.Vector2(self.rect.topleft)
                        self.click_move_target_pos = clamped_target_pos
                        self.click_move_start_time = current_time
                        self.is_click_moving = True
                        self.Goto = pygame.math.Vector2(0, 0) # Ensure keyboard move stops
                        self.ismoving = False

        # --- Cancel Key --- (Handles deselect or cancelling other states)
        if self.input_manager.is_just_pressed('Cancel'):
            if hasattr(self.level.map_action, 'current_dialog') and self.level.map_action.current_dialog:
                return # Don't process cancel if dialog is open

            if self.SW_select:
                selected_battler = self.level.map_action.selected_battler
                if (self.level.map_action.current_state == 'player_control' and selected_battler):
                    # Initiate timed move back to the selected battler's tile
                    target_px = selected_battler.pos.x * TILESIZE
                    target_py = selected_battler.pos.y * TILESIZE
                    target_pos_vec = pygame.math.Vector2(target_px, target_py)
                    if target_pos_vec != self.rect.topleft:
                         self.click_move_start_pos = pygame.math.Vector2(self.rect.topleft)
                         self.click_move_target_pos = target_pos_vec
                         self.click_move_start_time = pygame.time.get_ticks()
                         self.is_click_moving = True
                         self.Goto = pygame.math.Vector2(0, 0) # Ensure keyboard move stops
                         self.ismoving = False
                    # Don't immediately set SW_select = False, wait for move to finish? Or allow interruption?
                    # For now, let the state handle the logic after cancel press.
                else: # explore or other states
                     self.SW_select = False # Just deselect immediately

            self.held_key = None # Stop keyboard movement

        # --- Select Key --- (Only if not moving via keyboard or mouse)
        if not self.select_lock and not self.move_lock and self.Goto.magnitude() == 0 and not self.is_click_moving:
            if self.input_manager.is_just_pressed('Select') or self.clicked_self:
                if self.clicked_self and self.SW_select:
                     self.clicked_self = False
                elif self.clicked_self and not self.SW_select:
                     self.SW_select = True
                     self.clicked_self = False
                elif self.input_manager.is_just_pressed('Select'):
                     self.SW_select = not self.SW_select # Toggle selection


        # --- Previous/Next Ally ---
        if self.level.map_action.current_state == 'explore':
             wheel_movement = self.input_manager.get_wheel_movement()
             if self.input_manager.is_just_pressed('Previous') or self.input_manager.is_just_pressed('Next') or wheel_movement != 0:
                # (Logic for finding next ally remains the same)
                # ... find next_battler ...
                actable_allies = [b for b in self.level.battler_sprites if b.team == 'Ally' and not b.inactive]
                if not actable_allies: return
                actable_allies.sort(key=lambda x: list(CharacterDatabase.data.keys()).index(x.char_type))
                # ... (find current_battler_index logic) ...
                current_battler = None
                for battler in actable_allies:
                    if (battler.pos.x == self.pos.x and battler.pos.y == self.pos.y):
                         current_battler = battler
                         break
                if not current_battler: current_battler_index = -1
                else:
                    try: current_battler_index = actable_allies.index(current_battler)
                    except ValueError: current_battler_index = -1

                direction = 'Previous' if (self.input_manager.is_just_pressed('Previous') or wheel_movement > 0) else 'Next'
                delta = -1 if direction == 'Previous' else 1
                if current_battler_index == -1: next_index = 0 if direction == 'Next' else len(actable_allies) - 1
                else: next_index = (current_battler_index + delta) % len(actable_allies)
                next_battler = actable_allies[next_index]

                # Use focus_on_target for smooth camera AND cursor move
                self.level.visible_sprites.focus_on_target(next_battler, cursor_obj=self)
                # Stop any previous movement
                self.Goto = pygame.math.Vector2(0, 0)
                self.ismoving = False
                self.is_click_moving = False # Ensure timed move is also stopped

    def move(self):
        current_time = pygame.time.get_ticks()
        previous_logical_pos = self.pos.copy() # Store logical pos before movement

        if self.is_click_moving:
            # --- Timed Mouse/Focus Movement (Linear Interpolation) ---
            elapsed_time = current_time - self.click_move_start_time
            duration = self.click_move_duration

            if elapsed_time >= duration:
                # Movement finished - Snap to final target
                self.rect.topleft = self.click_move_target_pos
                self.is_click_moving = False

                # Update logical pos AFTER snapping
                self.pos = pygame.math.Vector2(self.rect.x // TILESIZE, self.rect.y // TILESIZE)
                if self.pos != previous_logical_pos and not self.move_lock: # Check if logical position changed
                     self.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_MOVE'])
                self.previous_pos = self.pos.copy()
            else:
                # Interpolate position
                t = elapsed_time / duration
                t = max(0.0, min(1.0, t)) # Clamp t between 0 and 1

                # Linear interpolation: P = P_start + t * (P_end - P_start)
                interp_x = self.click_move_start_pos.x + (self.click_move_target_pos.x - self.click_move_start_pos.x) * t
                interp_y = self.click_move_start_pos.y + (self.click_move_target_pos.y - self.click_move_start_pos.y) * t
                self.rect.topleft = (interp_x, interp_y)

            # Update collision rect during interpolation too
            self.collision_rect.topleft = self.rect.topleft

        elif self.Goto.magnitude() > 0:
            # --- Keyboard Movement (Incremental) ---
            move_speed = self.move_per_tile
            move_vector = self.Goto.normalize() * move_speed
            if move_vector.magnitude() >= self.Goto.magnitude():
                move_vector = self.Goto # Prevent overshoot

            # Boundary checks (same as before)
            next_x = self.rect.x + move_vector.x
            next_y = self.rect.y + move_vector.y
            max_px = self.level_data["Map_Max_x"] - TILESIZE
            max_py = self.level_data["Map_Max_y"] - TILESIZE
            if next_x < 0: move_vector.x = -self.rect.x; self.Goto.x = 0
            elif next_x > max_px: move_vector.x = max_px - self.rect.x; self.Goto.x = 0
            if next_y < 0: move_vector.y = -self.rect.y; self.Goto.y = 0
            elif next_y > max_py: move_vector.y = max_py - self.rect.y; self.Goto.y = 0

            # Apply movement
            self.rect.x += move_vector.x
            self.rect.y += move_vector.y
            self.collision_rect.topleft = self.rect.topleft
            self.Goto -= move_vector

            # Snap and finalize if movement complete
            if self.Goto.magnitude() < 1.0:
                self.rect.topleft = (round(self.rect.x), round(self.rect.y)) # Snap
                self.collision_rect.topleft = self.rect.topleft
                self.Goto = pygame.math.Vector2(0, 0)
                self.ismoving = False # Keyboard move finished

                # Update logical pos AFTER snapping
                self.pos = pygame.math.Vector2(self.rect.x // TILESIZE, self.rect.y // TILESIZE)
                if self.pos != previous_logical_pos and not self.move_lock: # Check if logical position changed
                     self.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_MOVE'])
                self.previous_pos = self.pos.copy()
        else:
            # No movement command active
            self.ismoving = False # Ensure flags are correct


    # draw_rect remains the same
    def draw_rect(self):
        if self.cached_image is None or self.cached_selection_state != self.SW_select:
            self.cached_selection_state = self.SW_select
            self.cached_image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            color = CURSOR_SELECTED_COLOR if self.SW_select else CURSOR_BORDER_COLOR
            pygame.draw.rect(self.cached_image, color, (0, 0, TILESIZE, TILESIZE), 8)
            pygame.draw.rect(self.cached_image, CURSOR_BASIC_COLOR, pygame.Rect(3, 3, TILESIZE - 6, TILESIZE - 6), 2)
            # Transparent center parts (optimization?) - keep if intended
            pygame.draw.rect(self.cached_image, (0,0,0,0), (16, 0, 32, 64))
            pygame.draw.rect(self.cached_image, (0,0,0,0), (0, 16, 64, 32))
        self.image = self.cached_image.copy()

    def update(self):
        self.handle_input()
        self.move()
        self.draw_rect()

    def start_timed_move(self, target_pixel_pos):
        """External function call to initiate a timed move (e.g., from focus_on_target)."""
        # Clamp target to boundaries
        max_px = self.level_data["Map_Max_x"] - TILESIZE
        max_py = self.level_data["Map_Max_y"] - TILESIZE
        clamped_target_x = max(0, min(target_pixel_pos.x, max_px))
        clamped_target_y = max(0, min(target_pixel_pos.y, max_py))
        clamped_target = pygame.math.Vector2(clamped_target_x, clamped_target_y)

        if clamped_target != self.rect.topleft:
            self.click_move_start_pos = pygame.math.Vector2(self.rect.topleft)
            self.click_move_target_pos = clamped_target
            self.click_move_start_time = pygame.time.get_ticks()
            self.is_click_moving = True
            self.Goto = pygame.math.Vector2(0, 0) # Stop keyboard movement
            self.ismoving = False