import asyncio
import pygame
import random
import math
import time
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class MathBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(50, 80)
        self.speed = random.uniform(1.5, 3.5)
        self.color = random.choice([BLUE, GREEN, RED, YELLOW, PURPLE, ORANGE, PINK, CYAN])
        self.pulse = 0
        self.generate_problem()

    def generate_problem(self):
        """Generate medium-hard level math problems"""
        problem_type = random.choice(['add', 'sub', 'mul', 'div', 'square', 'power', 'fraction', 'mixed'])

        if problem_type == 'add':
            self.num1 = random.randint(45, 150)
            self.num2 = random.randint(35, 120)
            self.answer = self.num1 + self.num2
            self.question = f"{self.num1} + {self.num2}"

        elif problem_type == 'sub':
            self.num1 = random.randint(80, 200)
            self.num2 = random.randint(30, self.num1 + 20)
            self.answer = self.num1 - self.num2
            self.question = f"{self.num1} - {self.num2}"

        elif problem_type == 'mul':
            self.num1 = random.randint(12, 25)
            self.num2 = random.randint(11, 20)
            self.answer = self.num1 * self.num2
            self.question = f"{self.num1} x {self.num2}"

        elif problem_type == 'div':
            self.num2 = random.randint(8, 15)
            self.answer = random.randint(12, 25)
            self.num1 = self.num2 * self.answer
            self.question = f"{self.num1} / {self.num2}"

        elif problem_type == 'square':
            self.num1 = random.randint(8, 15)
            self.answer = self.num1 * self.num1
            self.question = f"{self.num1}²"

        elif problem_type == 'power':
            base = random.randint(3, 8)
            power = random.randint(2, 3)
            self.answer = base ** power
            self.question = f"{base}^{power}"

        elif problem_type == 'fraction':
            denominators = [2, 4, 5, 8, 10]
            denom = random.choice(denominators)
            numer = random.randint(1, denom * 3)
            self.answer = int((numer / denom) * 100)
            self.question = f"{numer}/{denom} as %"

        else:  # mixed operations
            operations = [
                lambda: self.generate_mixed_add_mul(),
                lambda: self.generate_mixed_sub_div(),
                lambda: self.generate_mixed_parentheses()
            ]
            random.choice(operations)()

    def generate_mixed_add_mul(self):
        a = random.randint(10, 30)
        b = random.randint(5, 12)
        c = random.randint(3, 8)
        self.answer = a + (b * c)
        self.question = f"{a} + {b} x {c}"

    def generate_mixed_sub_div(self):
        c = random.randint(2, 6)
        b = c * random.randint(4, 10)
        a = random.randint(20, 50)
        self.answer = a - (b // c)
        self.question = f"{a} - {b} / {c}"

    def generate_mixed_parentheses(self):
        a = random.randint(8, 20)
        b = random.randint(5, 15)
        c = random.randint(3, 7)
        self.answer = (a + b) * c
        self.question = f"({a} + {b}) x {c}"

    def update(self):
        self.y += self.speed
        self.pulse += 0.1

    def draw(self, screen, font):
        pulse_size = int(5 * math.sin(self.pulse))
        current_radius = self.radius + pulse_size

        # Draw ball with gradient effect
        for i in range(current_radius):
            color = tuple(max(0, min(255, c - i)) for c in self.color)
            if i < current_radius:
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), current_radius - i, 2)

        # Draw outer glow
        glow_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), current_radius + 5, 3)

        # Draw question text (clean, no shadow)
        text = font.render(self.question, True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)
        return distance <= self.radius

    def is_out_of_bounds(self):
        return self.y > SCREEN_HEIGHT + 100

class MathBallGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🎮 Math Ball Catcher - Medium-Hard Edition")
        self.clock = pygame.time.Clock()

        # Load fonts
        self.load_fonts()

        # Game state
        self.state = "menu"
        self.player_name = ""
        self.score = 0
        self.time_left = 90
        self.start_time = 0
        self.balls = []
        self.input_text = ""
        self.selected_ball = None
        self.particles = []
        self.stars = []
        self.last_answer_correct = None
        self.answer_feedback_timer = 0
        self.problems_solved = 0
        self.correct_answers = 0

        # Animation variables
        self.menu_animation = 0

        # Create background elements
        self.create_stars()

        # Load audio and images
        self.load_audio()
        self.load_background_image()

    def load_fonts(self):
        """Load fonts with emoji support"""
        try:
            # Try to load system fonts that support emojis
            font_names = ['segoeuiemoji', 'applesymbol', 'notocoloremoji', 'symbola', 'dejavusans']

            self.emoji_font = None
            for font_name in font_names:
                try:
                    test_font = pygame.font.SysFont(font_name, 32)
                    # Test if it can render emojis
                    test_surface = test_font.render("🎮", True, WHITE)
                    if test_surface.get_width() > 10:  # If emoji rendered properly
                        self.emoji_font = test_font
                        break
                except:
                    continue

            # If no emoji font found, try default system font
            if not self.emoji_font:
                try:
                    self.emoji_font = pygame.font.SysFont('arial', 32)
                except:
                    self.emoji_font = None

        except:
            self.emoji_font = None

        # Regular fonts
        self.font_large = pygame.font.Font(None, 42)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 26)
        self.font_title = pygame.font.Font(None, 84)
        self.font_huge = pygame.font.Font(None, 120)

    def draw_text_with_emoji(self, text, font, color, pos):
        """Draw text with emoji support - ONLY CHANGED THIS FUNCTION"""
        # First try to render with emoji font
        if self.emoji_font:
            try:
                rendered_text = self.emoji_font.render(text, True, color)
                self.screen.blit(rendered_text, pos)
                return
            except:
                pass

        # If emoji font fails, try regular font with original emojis
        try:
            rendered_text = font.render(text, True, color)
            self.screen.blit(rendered_text, pos)
            return
        except:
            pass

        # Final fallback: replace emojis with symbols
        icon_replacements = {
            '🎮': '♦', '🎯': '◎', '🧮': '≡', '⏰': '⌚', '🌟': '★', '🚀': '↑',
            '💰': '$', '👤': '@', '🎈': 'O', '✅': '✓', '❌': '✗', '🤔': '?',
            '⌨️': '⌨', '🏆': '♔', '👏': '♪', '📚': '■', '🔄': '↻', '🎵': '♫',
            '🔊': '♪', '🎨': '◊', '💻': '□', '👍': '+', '💪': '!', '📖': '▣',
            '🧠': '◉', '⚡': '⚡', '🔥': '※', '💡': '◐', '🎓': '▲'
        }

        display_text = text
        for emoji, replacement in icon_replacements.items():
            display_text = display_text.replace(emoji, replacement)

        rendered_text = font.render(display_text, True, color)
        self.screen.blit(rendered_text, pos)

    def load_audio(self):
        """Load audio files if they exist"""
        try:
            if os.path.exists("background_music.mp3"):
                pygame.mixer.music.load("background_music.mp3")
                self.has_bg_music = True
            elif os.path.exists("background_music.wav"):
                pygame.mixer.music.load("background_music.wav")
                self.has_bg_music = True
            else:
                self.has_bg_music = False

            self.sound_correct = pygame.mixer.Sound("correct.wav") if os.path.exists("correct.wav") else None
            self.sound_wrong = pygame.mixer.Sound("wrong.wav") if os.path.exists("wrong.wav") else None
            self.sound_game_over = pygame.mixer.Sound("game_over.wav") if os.path.exists("game_over.wav") else None

        except Exception as e:
            self.has_bg_music = False
            self.sound_correct = None
            self.sound_wrong = None
            self.sound_game_over = None

    def load_background_image(self):
        """Load background image if it exists"""
        try:
            if os.path.exists("background.jpg"):
                self.bg_image = pygame.image.load("background.jpg")
                self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.has_bg_image = True
            elif os.path.exists("background.png"):
                self.bg_image = pygame.image.load("background.png")
                self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.has_bg_image = True
            else:
                self.has_bg_image = False
        except Exception as e:
            self.has_bg_image = False

    def play_sound(self, sound_type):
        """Play sound effects"""
        try:
            if sound_type == "correct" and self.sound_correct:
                self.sound_correct.play()
            elif sound_type == "wrong" and self.sound_wrong:
                self.sound_wrong.play()
            elif sound_type == "game_over" and self.sound_game_over:
                self.sound_game_over.play()
        except Exception as e:
            pass

    def start_background_music(self):
        """Start background music"""
        try:
            if self.has_bg_music:
                pygame.mixer.music.play(-1)
        except Exception as e:
            pass

    def create_stars(self):
        for _ in range(200):
            star = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'brightness': random.randint(100, 255),
                'twinkle': random.uniform(0, 2 * math.pi),
                'size': random.randint(1, 4)
            }
            self.stars.append(star)

    def update_stars(self):
        for star in self.stars:
            star['twinkle'] += 0.05
            star['brightness'] = int(150 + 105 * math.sin(star['twinkle']))

    def draw_background(self):
        if self.has_bg_image:
            self.screen.blit(self.bg_image, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 60))
            self.screen.blit(overlay, (0, 0))
        else:
            for y in range(SCREEN_HEIGHT):
                color_ratio = y / SCREEN_HEIGHT
                time_offset = math.sin(time.time() * 0.3) * 0.3
                r = max(0, min(255, int(25 + (50 * (color_ratio + time_offset)))))
                g = max(0, min(255, int(35 + (70 * (color_ratio + time_offset)))))
                b = max(0, min(255, int(90 + (140 * (color_ratio + time_offset)))))
                pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Draw twinkling stars
        self.update_stars()
        for star in self.stars:
            color = (star['brightness'], star['brightness'], star['brightness'])
            pygame.draw.circle(self.screen, color, (star['x'], star['y']), star['size'])

    def create_particle_explosion(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw_particles(self):
        for particle in self.particles:
            particle.draw(self.screen)

    def draw_menu(self):
        self.draw_background()
        self.menu_animation += 0.02

        # Animated title with rainbow effect
        title_y = 160 + math.sin(self.menu_animation) * 20
        colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
        title_text = "MATH BALL CATCHER"

        for i, char in enumerate(title_text):
            color = colors[i % len(colors)]
            char_surface = self.font_title.render(char, True, color)
            char_y = title_y + math.sin(self.menu_animation + i * 0.4) * 15
            char_x = 280 + i * 45
            self.screen.blit(char_surface, (char_x, char_y))

        # Subtitle
        subtitle_surface = self.font_large.render("MEDIUM-HARD EDITION", True, YELLOW)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH//2, title_y + 100))
        self.screen.blit(subtitle_surface, subtitle_rect)

        # Instructions
        instructions = [
            "🧠 Challenge your brain with medium-hard math problems!",
            "⚡ Solve complex equations: squares, powers, fractions & more",
            "🔥 90 seconds to prove your mathematical prowess!",
            "🎯 Higher difficulty = Higher rewards (+5 correct, -2 wrong)",
            "",
            "🚀 Press SPACE to begin the ultimate math challenge!"
        ]

        for i, instruction in enumerate(instructions):
            self.draw_text_with_emoji(instruction, self.font_medium, WHITE,
                                    (SCREEN_WIDTH//2 - len(instruction) * 7, 350 + i * 40))

    def draw_name_input(self):
        self.draw_background()

        # Title
        self.draw_text_with_emoji("🎮 Enter Your Math Champion Name:", self.font_large, YELLOW,
                                (SCREEN_WIDTH//2 - 250, 280))

        # # Difficulty indicator
        # difficulty_text = self.font_medium.render("🧠 DIFFICULTY: MEDIUM-HARD 🔥", True, ORANGE)
        # difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, 320))
        # self.screen.blit(difficulty_text, difficulty_rect)

        # Input box
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 220, 360, 440, 70)
        pygame.draw.rect(self.screen, WHITE, input_box)
        pygame.draw.rect(self.screen, BLUE, input_box, 5)

        # Input text with cursor
        display_name = self.player_name + ("|" if int(time.time() * 2) % 2 else "")
        text = self.font_large.render(display_name, True, BLACK)
        text_rect = text.get_rect(center=input_box.center)
        self.screen.blit(text, text_rect)

        # Instructions
        instruction = self.font_small.render("Press ENTER to start your mathematical journey!", True, WHITE)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, 480))
        self.screen.blit(instruction, instruction_rect)

    def draw_game(self):
        self.draw_background()
        self.update_particles()
        self.draw_particles()

        # Draw balls
        for ball in self.balls:
            ball.draw(self.screen, self.font_medium)

        # UI elements
        # Score display
        score_bg = pygame.Rect(15, 15, 300, 55)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), score_bg)
        pygame.draw.rect(self.screen, YELLOW, score_bg, 4)

        score_color = GREEN if self.score >= 0 else RED
        self.draw_text_with_emoji(f"💰 Score: {self.score}", self.font_large, score_color, (25, 25))

        # Time display
        time_bg = pygame.Rect(15, 80, 300, 55)
        time_color = RED if self.time_left < 20 else ORANGE if self.time_left < 45 else GREEN

        pygame.draw.rect(self.screen, (0, 0, 0, 180), time_bg)
        pygame.draw.rect(self.screen, time_color, time_bg, 4)

        self.draw_text_with_emoji(f"⏰ Time: {int(self.time_left)}", self.font_large, time_color, (25, 90))

        # Player name
        name_bg = pygame.Rect(15, 150, 300, 55)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), name_bg)
        pygame.draw.rect(self.screen, CYAN, name_bg, 4)
        self.draw_text_with_emoji(f"👤 {self.player_name}", self.font_medium, WHITE, (25, 163))

        # Statistics
        stats_bg = pygame.Rect(15, 220, 300, 55)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), stats_bg)
        pygame.draw.rect(self.screen, PURPLE, stats_bg, 4)
        accuracy = int((self.correct_answers / max(1, self.problems_solved)) * 100)
        self.draw_text_with_emoji(f"🎯 Accuracy: {accuracy}%", self.font_medium, WHITE, (25, 230))

        # Ball count and difficulty
        self.draw_text_with_emoji(f"🎈 Active: {len(self.balls)}", self.font_small, WHITE,
                                (SCREEN_WIDTH - 180, 25))

        # Answer feedback (clean, no black overlay)
        if self.answer_feedback_timer > 0:
            self.draw_answer_feedback()
            self.answer_feedback_timer -= 1

        # Answer popup
        if self.selected_ball:
            self.draw_answer_popup()

    def draw_answer_feedback(self):
        """Draw clean feedback for correct/wrong answers"""
        if self.last_answer_correct is not None:
            feedback_y = 180 + math.sin(time.time() * 10) * 15

            if self.last_answer_correct:
                feedback_text = "CORRECT! +5 points"
                feedback_color = GREEN
            else:
                feedback_text = "WRONG! -2 points"
                feedback_color = RED

            # Clean text display (no black overlay)
            text_surface = self.font_large.render(feedback_text, True, feedback_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, feedback_y))
            self.screen.blit(text_surface, text_rect)

    def draw_answer_popup(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Popup box
        popup_box = pygame.Rect(SCREEN_WIDTH//2 - 500, 220, 1000, 450)

        # Gradient background
        for i in range(popup_box.height):
            color_ratio = i / popup_box.height
            r = max(0, min(255, int(60 + (120 * color_ratio))))
            g = max(0, min(255, int(30 + (90 * color_ratio))))
            b = max(0, min(255, int(120 + (180 * color_ratio))))
            pygame.draw.line(self.screen, (r, g, b),
                           (popup_box.x, popup_box.y + i),
                           (popup_box.x + popup_box.width, popup_box.y + i))

        # Border
        pygame.draw.rect(self.screen, WHITE, popup_box, 5)

        # Difficulty indicator
        self.draw_text_with_emoji("🧠 HARD PROBLEM 🔥", self.font_medium, ORANGE,
                                (SCREEN_WIDTH//2 - 175, 250))

        # Question display (clean, no black text)
        question_text = f"{self.selected_ball.question} = ?"
        text_surface = self.font_huge.render(question_text, True, YELLOW)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 340))
        self.screen.blit(text_surface, text_rect)

        # Answer input box
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 250, 400, 500, 100)
        pygame.draw.rect(self.screen, WHITE, input_box)
        pygame.draw.rect(self.screen, BLUE, input_box, 5)

        # Input text with cursor
        display_text = self.input_text + ("|" if int(time.time() * 4) % 2 else "")
        text = self.font_large.render(display_text, True, BLACK)
        text_rect = text.get_rect(center=input_box.center)
        self.screen.blit(text, text_rect)

        # Instructions
        self.draw_text_with_emoji("⌨️ Type your answer and press ENTER", self.font_medium, WHITE,
                                (SCREEN_WIDTH//2 - 275, 540))

        # Hint
        self.draw_text_with_emoji("💡 Remember: Order of operations matters!", self.font_small, CYAN,
                                (SCREEN_WIDTH//2 - 275, 570))

    def draw_game_over(self):
        self.draw_background()
        self.update_particles()
        self.draw_particles()

        # Game over text
        game_over_y = 120 + math.sin(time.time() * 2) * 15

        # Performance-based message
        accuracy = int((self.correct_answers / max(1, self.problems_solved)) * 100)

        if self.score >= 150 and accuracy >= 80:
            title = "🏆 MATH GENIUS! 🧠"
            title_color = YELLOW
            message = "🌟 Outstanding mathematical mastery! 🌟"
        elif self.score >= 100 and accuracy >= 70:
            title = "🔥 MATH EXPERT! 🔥"
            title_color = ORANGE
            message = "⚡ Excellent problem-solving skills! ⚡"
        elif self.score >= 60 and accuracy >= 60:
            title = "🌟 MATH SCHOLAR! 📚"
            title_color = GREEN
            message = "👏 Great mathematical thinking! 👏"
        elif self.score >= 30:
            title = "👍 MATH STUDENT! 📖"
            title_color = CYAN
            message = "💪 Keep practicing those hard problems! 💪"
        else:
            title = "🎯 MATH LEARNER! 🎓"
            title_color = PURPLE
            message = "🚀 Challenge yourself with more practice! 🚀"

        # Title
        self.draw_text_with_emoji(title, self.font_title, title_color,
                                (SCREEN_WIDTH//2 - 170, game_over_y))

        # Statistics display
        stats_y = 220

        # Final score
        self.draw_text_with_emoji(f"🎯 Final Score: {self.score} points", self.font_large, WHITE,
                                (SCREEN_WIDTH//2 - 180, stats_y))

        # Player name
        self.draw_text_with_emoji(f"👤 Player: {self.player_name}", self.font_medium, CYAN,
                                (SCREEN_WIDTH//2 - 140, stats_y + 60))

        # Problems solved
        self.draw_text_with_emoji(f"🧮 Problems Solved: {self.problems_solved}", self.font_medium, WHITE,
                                (SCREEN_WIDTH//2 - 180, stats_y + 120))

        # Accuracy percentage
        accuracy_color = GREEN if accuracy >= 70 else ORANGE if accuracy >= 50 else RED
        self.draw_text_with_emoji(f"🎯 Accuracy: {accuracy}%", self.font_medium, accuracy_color,
                                (SCREEN_WIDTH//2 - 140, stats_y + 180))

        # Performance message
        self.draw_text_with_emoji(message, self.font_medium, WHITE,
                                (SCREEN_WIDTH//2 - 270, stats_y + 240))

        # Restart instructions
        self.draw_text_with_emoji("🔄 Press SPACE to play again or ESC to quit", self.font_medium, WHITE,
                                (SCREEN_WIDTH//2 - 300, stats_y + 300))

    def spawn_ball(self):
        if len(self.balls) < 8:
            x = random.randint(80, SCREEN_WIDTH - 80)
            y = random.randint(-120, -60)
            self.balls.append(MathBall(x, y))
            
    def update_game(self):
        current_time = time.time()
        self.time_left = 30 - (current_time - self.start_time)

        if self.time_left <= 0:
            self.state = "game_over"
            self.play_sound("game_over")
            self.create_particle_explosion(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, YELLOW, 40)
            return

        # Update balls and check if selected ball is out of bounds
        for ball in self.balls[:]:
            ball.update()
            if ball.is_out_of_bounds():
                # If the selected ball goes out of bounds, close the popup
                if self.selected_ball == ball:
                    self.selected_ball = None
                    self.input_text = ""
                self.balls.remove(ball)

        # Spawn balls randomly (like raindrops)
        spawn_probability = 0.025 if len(self.balls) < 4 else 0.015
        if random.random() < spawn_probability:
            self.spawn_ball()

    def handle_ball_click(self, pos):
        for ball in self.balls:
            if ball.is_clicked(pos):
                self.selected_ball = ball
                self.input_text = ""
                self.create_particle_explosion(ball.x, ball.y, ball.color, 12)
                break

    def check_answer(self):
        try:
            # Handle both integer and decimal answers
            if '.' in str(self.selected_ball.answer):
                user_answer = float(self.input_text)
                correct = abs(user_answer - self.selected_ball.answer) < 0.01
            else:
                user_answer = int(self.input_text)
                correct = user_answer == self.selected_ball.answer

            self.problems_solved += 1

            if correct:
                self.score += 5
                self.correct_answers += 1
                self.last_answer_correct = True
                self.play_sound("correct")
                self.create_particle_explosion(self.selected_ball.x, self.selected_ball.y, GREEN, 25)
            else:
                self.score -= 2
                self.last_answer_correct = False
                self.play_sound("wrong")
                self.create_particle_explosion(self.selected_ball.x, self.selected_ball.y, RED, 20)

            # Set feedback timer
            self.answer_feedback_timer = 150

            self.balls.remove(self.selected_ball)
            self.selected_ball = None
            self.input_text = ""
        except ValueError:
            pass

    async def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if self.state == "menu":
                        if event.key == pygame.K_SPACE:
                            self.state = "name_input"

                    elif self.state == "name_input":
                        if event.key == pygame.K_RETURN and self.player_name.strip():
                            self.state = "game"
                            self.start_time = time.time()
                            self.score = 0
                            self.balls = []
                            self.particles = []
                            self.last_answer_correct = None
                            self.answer_feedback_timer = 0
                            self.problems_solved = 0
                            self.correct_answers = 0
                            self.start_background_music()
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        else:
                            if len(self.player_name) < 25 and event.unicode.isprintable():
                                self.player_name += event.unicode

                    elif self.state == "game":
                        if self.selected_ball:
                            if event.key == pygame.K_RETURN:
                                self.check_answer()
                            elif event.key == pygame.K_BACKSPACE:
                                self.input_text = self.input_text[:-1]
                            elif event.unicode.isdigit() or event.unicode in '.-':
                                if len(self.input_text) < 10:
                                    # Allow negative numbers and decimals
                                    if event.unicode == '-' and self.input_text:
                                        pass  # Don't allow minus in middle
                                    elif event.unicode == '.' and '.' in self.input_text:
                                        pass  # Don't allow multiple decimals
                                    else:
                                        self.input_text += event.unicode

                    elif self.state == "game_over":
                        if event.key == pygame.K_SPACE:
                            self.state = "name_input"
                            self.player_name = ""
                            pygame.mixer.music.stop()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "game" and not self.selected_ball:
                        self.handle_ball_click(event.pos)

            # Update game state
            if self.state == "game":
                self.update_game()

            # Draw everything
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "name_input":
                self.draw_name_input()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.flip()
            await asyncio.sleep(0)
            self.clock.tick(60)

        pygame.quit()

async def main():
    game = MathBallGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())