# TURTLE STACK
# by Bryan Wieschenberg

# This game was made in under 24 hours for the HackTCNJ 2025 Hackathon

# The game is about turtles and is a simple stacking game where the player must stack up turtles
# The player loses HP if a turtle falls off the screen or if the turtle misses the platform

# The player can stack turtles of different colors, each with their own unique properties
#   Green turtles fall normally
#   Blue turtles bounce off the platform once before being stackable
#   Pink turtles quickly displace after falling a certain distance
#   Orange turtles quickly come in from a low side instead of from the top of the screen
#   Yellow turtles grant the player back HP, and are particularly hard to catch, but missing them has HP no penalty
#   Red turtles spawn 2 falsely-colored clones around the real turtle, but only the real one can be caught
#   Purple turtles will fade away as they fall

# Stacking functionality could not be implemented due to time constraints
# I will continue to work on this game and add this feature, among more, in the future

import pygame
import os
import tkinter as tk
import random

# Initialize Pygame
pygame.init()
dir = os.path.dirname(os.path.abspath(__file__))
root = tk.Tk()
WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turtle Stack")
clock = pygame.time.Clock()

# Animation
frames = []
frame_files = sorted(os.listdir(os.path.join(dir, "assets", "water")),
key=lambda f: int(''.join(filter(str.isdigit, f))))
for file in frame_files:
    frames.append(pygame.image.load(os.path.join(dir, "assets", "water", file)))
current_frame = 0
frame_delay = 3
frame_timer = 0
water_width, water_height = frames[0].get_size()
water_width, water_height = int(water_width * 0.25), int(water_height * 0.25)

# Colors and scoring
BLUE = (149, 255, 230)
score = 0
extra_hit_points = 5  # Extra hit point buffer granted by yellow turtle

# Platform
platform_width = WIDTH // 10
platform_height = HEIGHT // 12
platform_x = (WIDTH - platform_width) // 2
platform_y = HEIGHT - platform_height - HEIGHT // 24

# Turtle dimensions
turtle_dimensions = {
    "green": (WIDTH//10, WIDTH//10),
    "blue": (WIDTH//12, WIDTH//12),
    "pink": (WIDTH//16, WIDTH//16),
    "orange": (WIDTH//24, WIDTH//24),
    "red": (WIDTH//12, WIDTH//12),
    "purple": (WIDTH//14, WIDTH//14),
    "yellow": (WIDTH//20, WIDTH//20)
}

# Turtle images
green_turtle_img = pygame.transform.scale(
    pygame.image.load(os.path.join(dir, "assets", "turtle_green.png")),
    turtle_dimensions["green"]
)
blue_turtle_img = pygame.transform.scale(
    pygame.image.load(os.path.join(dir, "assets", "turtle_blue.png")),
    turtle_dimensions["blue"]
)
pink_turtle_img = pygame.transform.scale(
    pygame.image.load(os.path.join(dir, "assets", "turtle_pink.png")),
    turtle_dimensions["pink"]
)
orange_turtle_img = pygame.transform.scale(
    pygame.image.load(os.path.join(dir, "assets", "turtle_orange.png")),
    turtle_dimensions["orange"]
)
red_turtle_img = pygame.transform.scale(
    pygame.image.load(os.path.join(dir, "assets", "turtle_red.png")),
    turtle_dimensions["red"]
).convert_alpha()
purple_turtle_img = pygame.transform.scale(
    pygame.image.load(os.path.join(dir, "assets", "turtle_purple.png")),
    turtle_dimensions["purple"]
).convert_alpha()
yellow_turtle_img = pygame.transform.scale(
    pygame.image.load(os.path.join(dir, "assets", "turtle_yellow.png")),
    turtle_dimensions["yellow"]
)

# Create clone images
def create_clone_image(base_image, color_shift):
    clone = base_image.copy()
    clone.fill(color_shift, special_flags=pygame.BLEND_RGB_ADD)
    return clone.convert_alpha()

red_clone_img = create_clone_image(red_turtle_img, (60, 60, 60))

# Turtle properties
turtles = []
base_speed = HEIGHT // 120

# Physics constants
GRAVITY = 0.5
BOUNCE_VELOCITY = -HEIGHT // 40

# Game Loop
running = True
while running:
    screen.fill(BLUE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Platform movement (speed increases with score)
    platform_speed = WIDTH // 60 + score // 5
    keys = pygame.key.get_pressed()
    platform_x = max(0, min(WIDTH - platform_width, platform_x + (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * platform_speed))

    # Draw platform
    pygame.draw.rect(screen, (139, 69, 19), (platform_x, platform_y, platform_width, platform_height))

    # Spawn turtles if none exist
    if not turtles:
        turtle_type = random.choice(["green", "blue", "pink", "orange", "red", "purple", "yellow"])
        
        if turtle_type == "red":
            width, height = turtle_dimensions["red"]
            spacing = WIDTH // 8
            total_width = 3 * width + 2 * spacing
            start_x = (WIDTH - total_width) // 2
            start_x = max(100, min(start_x, WIDTH - total_width - 100))
            positions = [
                {"x": start_x, "is_real": False},
                {"x": start_x + width + spacing, "is_real": False},
                {"x": start_x + 2 * (width + spacing), "is_real": False}
            ]
            real_index = random.randint(0, 2)
            positions[real_index]["is_real"] = True
            turtle_group = []
            for pos in positions:
                turtle_group.append({
                    "type": "red",
                    "image": red_turtle_img if pos["is_real"] else red_clone_img,
                    "is_real": pos["is_real"],
                    "x": pos["x"],
                    "y": -height,
                    "velocity": 0,
                    "width": width,
                    "height": height
                })
            random.shuffle(turtle_group)
            turtles.extend(turtle_group)
        elif turtle_type == "purple":
            width, height = turtle_dimensions["purple"]
            new_turtle = {
                "type": "purple",
                "image": purple_turtle_img.copy(),
                "x": random.randint(50, WIDTH - width - 50),
                "y": -height,
                "velocity": 0,
                "width": width,
                "height": height,
                "alpha": 255,
                "initial_y": -height
            }
            turtles.append(new_turtle)
        elif turtle_type == "orange":
            width, height = turtle_dimensions["orange"]
            side_from_left = random.choice([True, False])
            new_turtle = {
                "type": "orange",
                "image": orange_turtle_img,
                "x": -width if side_from_left else WIDTH,
                "y": random.randint(HEIGHT // 4, HEIGHT // 3),
                "velocity": 0,
                "width": width,
                "height": height,
                "h_velocity": (WIDTH // 100) if side_from_left else -(WIDTH // 100)
            }
            turtles.append(new_turtle)
        elif turtle_type == "yellow":
            width, height = turtle_dimensions["yellow"]
            new_turtle = {
                "type": "yellow",
                "image": yellow_turtle_img,
                "x": random.randint(50, WIDTH - width - 50),
                "y": -height,
                "velocity": base_speed * 3,
                "width": width,
                "height": height
            }
            turtles.append(new_turtle)
        else:
            width, height = turtle_dimensions[turtle_type]
            new_turtle = {
                "type": turtle_type,
                "image": {
                    "green": green_turtle_img,
                    "blue": blue_turtle_img,
                    "pink": pink_turtle_img
                }[turtle_type],
                "x": random.randint(50, WIDTH - width - 50),
                "y": -height,
                "velocity": 0,
                "bounces": 0,
                "h_velocity": random.choice([-1, 1]) * (WIDTH // 100) if turtle_type == "blue" else 0,
                "jumped": False,
                "initial_y": -height,
                "width": width,
                "height": height
            }
            if turtle_type == "pink":
                new_turtle["jumped"] = False
                new_turtle["initial_y"] = -height
            turtles.append(new_turtle)
    
    # Update and draw turtles
    current_speed = base_speed + (score // 2)
    for turtle in turtles[:]:
        if turtle["type"] == "green":
            turtle["y"] += current_speed
        elif turtle["type"] == "blue":
            turtle["velocity"] += GRAVITY
            turtle["y"] += turtle["velocity"]
            turtle["x"] += turtle["h_velocity"] * (1 + score / 100.0)
            if turtle["x"] <= 0:
                turtle["x"] = 0
                turtle["h_velocity"] = abs(turtle["h_velocity"])
            elif turtle["x"] >= WIDTH - turtle["width"]:
                turtle["x"] = WIDTH - turtle["width"]
                turtle["h_velocity"] = -abs(turtle["h_velocity"])
        elif turtle["type"] == "pink":
            turtle["y"] += current_speed
            distance_fallen = turtle["y"] - turtle["initial_y"]
            if not turtle["jumped"] and distance_fallen >= HEIGHT // 3:
                jump_offset = random.choice([-200, 200])
                new_x = turtle["x"] + jump_offset
                turtle["x"] = max(0, min(WIDTH - turtle["width"], new_x))
                turtle["jumped"] = True
        elif turtle["type"] == "orange":
            turtle["velocity"] += GRAVITY * 0.3
            turtle["y"] += turtle["velocity"]
            turtle["x"] += turtle["h_velocity"] * (1 + score / 100.0)
            if turtle["x"] <= 0:
                turtle["x"] = 0
                turtle["h_velocity"] = abs(turtle["h_velocity"])
            elif turtle["x"] >= WIDTH - turtle["width"]:
                turtle["x"] = WIDTH - turtle["width"]
                turtle["h_velocity"] = -abs(turtle["h_velocity"])
        elif turtle["type"] == "yellow":
            turtle["y"] += turtle["velocity"]
        elif turtle["type"] == "red":
            turtle["y"] += current_speed
        elif turtle["type"] == "purple":
            turtle["y"] += current_speed
            fade_start_y = turtle["initial_y"]
            fade_end_y = HEIGHT // 3
            current_y = turtle["y"]
            fade_progress = (current_y - fade_start_y) / (fade_end_y - fade_start_y)
            turtle["alpha"] = max(0, 255 - int(255 * fade_progress))
            turtle["image"].set_alpha(turtle["alpha"])
        
        # Collision detection
        turtle_rect = pygame.Rect(turtle["x"], turtle["y"], turtle["width"], turtle["height"])
        platform_rect = pygame.Rect(platform_x, platform_y, platform_width, platform_height)
        
        if turtle_rect.colliderect(platform_rect):
            if turtle["type"] == "green":
                if turtle_rect.bottom <= platform_rect.top + platform_height // 2:
                    score += 1
                    turtles.remove(turtle)
                else:
                    # Check HP before resetting score
                    if extra_hit_points > 0:
                        extra_hit_points -= 1
                        turtles.remove(turtle)
                    else:
                        score = 0
                        turtles.remove(turtle)
            elif turtle["type"] == "blue":
                if turtle_rect.bottom <= platform_rect.top + platform_height // 2:
                    if turtle["bounces"] == 0:
                        turtle["velocity"] = BOUNCE_VELOCITY
                        turtle["bounces"] += 1
                        turtle["h_velocity"] = random.choice([-1, 1]) * (WIDTH // 100)
                    else:
                        score += 1
                        turtles.remove(turtle)
                else:
                    if extra_hit_points > 0:
                        extra_hit_points -= 1
                        turtles.remove(turtle)
                    else:
                        score = 0
                        turtles.remove(turtle)
            elif turtle["type"] == "pink":
                if turtle_rect.bottom <= platform_rect.top + platform_height // 2:
                    score += 1
                    turtles.remove(turtle)
                else:
                    if extra_hit_points > 0:
                        extra_hit_points -= 1
                        turtles.remove(turtle)
                    else:
                        score = 0
                        turtles.remove(turtle)
            elif turtle["type"] == "orange":
                if turtle_rect.bottom <= platform_rect.top + platform_height // 2:
                    score += 1
                    turtles.remove(turtle)
                else:
                    if extra_hit_points > 0:
                        extra_hit_points -= 1
                        turtles.remove(turtle)
                    else:
                        score = 0
                        turtles.remove(turtle)
            elif turtle["type"] == "yellow":
                if turtle_rect.bottom <= platform_rect.top + platform_height // 2:
                    score += 1
                    if extra_hit_points < 5:
                        extra_hit_points += 1
                    turtles.remove(turtle)
                else:
                    turtles.remove(turtle)
            elif turtle["type"] == "red":
                if turtle.get("is_real", False):
                    if turtle_rect.bottom <= platform_rect.top + platform_height // 2:
                        score += 1
                    else:
                        if extra_hit_points > 0:
                            extra_hit_points -= 1
                        else:
                            score = 0
                    turtles = [t for t in turtles if t["type"] != "red"]
                else:
                    if extra_hit_points > 0:
                        extra_hit_points -= 1
                    else:
                        score = 0
                    turtles = [t for t in turtles if t["type"] != "red"]
            elif turtle["type"] == "purple":
                if turtle_rect.bottom <= platform_rect.top + platform_height // 2:
                    score += 1
                else:
                    if extra_hit_points > 0:
                        extra_hit_points -= 1
                    else:
                        score = 0
                turtles.remove(turtle)
        elif turtle["y"] > HEIGHT:
            if turtle["type"] == "yellow":
                turtles.remove(turtle)
            else:
                if extra_hit_points > 0:
                    extra_hit_points -= 1
                    turtles.remove(turtle)
                else:
                    score = 0
                    if turtle["type"] == "red":
                        turtles = [t for t in turtles if t["type"] != "red"]
                    else:
                        turtles.remove(turtle)
        
        # Draw turtle
        screen.blit(turtle["image"], (turtle["x"], turtle["y"]))

    # Draw water animation
    frame_timer += 1
    if frame_timer >= frame_delay:
        current_frame = (current_frame + 1) % len(frames)
        frame_timer = 0
    x_position = 0
    while x_position < WIDTH:
        screen.blit(pygame.transform.scale(frames[current_frame],
                   (water_width, water_height)),
                   (x_position, HEIGHT - water_height))
        x_position += water_width
    
    # Score display
    font = pygame.font.Font(None, HEIGHT // 20)
    screen.blit(font.render(f"Score: {score}  HP: {extra_hit_points}", True, (0, 0, 0)), (WIDTH // 50, HEIGHT // 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
