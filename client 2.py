import pygame
import socket
import threading
import sys

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
COLORS = [BLACK, (255, 0, 0), (0, 255, 0), (0, 0, 255)]
BRUSH_SIZES = [5, 10, 15]

chat_messages = []
chat_input = ""

HOST = '127.0.0.1'
PORT = 5000

def receive_data(client_socket, screen, canvas):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data.startswith("MSG:"):
                chat_messages.append(data[4:])
            elif data.startswith("DRAW:"):
                # Drawing data format: DRAW:x1,y1,x2,y2,r,g,b,size
                parts = data[5:].split(",")
                x1, y1, x2, y2 = map(int, parts[:4])
                color = tuple(map(int, parts[4:7]))  # RGB color
                size = int(parts[7])
                pygame.draw.line(canvas, color, (x1, y1), (x2, y2), size)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

def send_data(client_socket, data):
    try:
        client_socket.send(data.encode())
    except Exception as e:
        print(f"Error sending data: {e}")

def draw_toolbar(screen):
    pygame.draw.rect(screen, GREY, (0, 0, WIDTH, 50))
    for i, size in enumerate(BRUSH_SIZES):
        pygame.draw.rect(screen, (220, 220, 220), (10 + i * 60, 10, 50, 30))
        font = pygame.font.Font(None, 24)
        text = font.render(str(size), True, BLACK)
        screen.blit(text, (25 + i * 60, 15))
    for i, color in enumerate(COLORS):
        pygame.draw.rect(screen, color, (WIDTH - 160 + i * 50, 10, 40, 30))

def draw_chat_box(screen):
    chat_box_rect = pygame.Rect(WIDTH - 310, HEIGHT - 160, 300, 150)
    pygame.draw.rect(screen, GREY, chat_box_rect)
    pygame.draw.rect(screen, BLACK, chat_box_rect, 2)
    font = pygame.font.Font(None, 24)
    y_offset = HEIGHT - 150
    for msg in reversed(chat_messages[-5:]):
        text = font.render(msg, True, BLACK)
        screen.blit(text, (WIDTH - 300, y_offset))
        y_offset += 30

def draw_input_box(screen, chat_input):
    input_box = pygame.Rect(10, HEIGHT - 40, WIDTH - 20, 30)
    pygame.draw.rect(screen, WHITE, input_box)
    pygame.draw.rect(screen, BLACK, input_box, 2)
    font = pygame.font.Font(None, 24)
    text_surface = font.render(chat_input, True, BLACK)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

def start_client():
    global chat_input
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Collaborative Drawing - Client 2")
    canvas = pygame.Surface((WIDTH, HEIGHT))
    canvas.fill(WHITE)

    clock = pygame.time.Clock()
    drawing = False
    prev_pos = None
    brush_color = BLACK
    brush_size = 5

    threading.Thread(target=receive_data, args=(client_socket, screen, canvas), daemon=True).start()

    while True:
        screen.fill(WHITE)
        screen.blit(canvas, (0, 0))
        draw_toolbar(screen)
        draw_chat_box(screen)
        draw_input_box(screen, chat_input)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] > 50:
                    drawing = True
                    prev_pos = event.pos
                else:
                    # Brush size selection
                    for i, size in enumerate(BRUSH_SIZES):
                        if 10 + i * 60 <= event.pos[0] <= 60 + i * 60 and 10 <= event.pos[1] <= 40:
                            brush_size = size
                    # Brush color selection
                    for i, color in enumerate(COLORS):
                        if WIDTH - 160 + i * 50 <= event.pos[0] <= WIDTH - 120 + i * 50 and 10 <= event.pos[1] <= 40:
                            brush_color = color

            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                prev_pos = None

            if event.type == pygame.MOUSEMOTION and drawing:
                current_pos = pygame.mouse.get_pos()
                pygame.draw.line(canvas, brush_color, prev_pos, current_pos, brush_size)
                # Send drawing data to the server
                send_data(client_socket, f"DRAW:{prev_pos[0]},{prev_pos[1]},{current_pos[0]},{current_pos[1]},{brush_color[0]},{brush_color[1]},{brush_color[2]},{brush_size}")
                prev_pos = current_pos

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and chat_input:
                    send_data(client_socket, f"MSG:{chat_input}")
                    chat_messages.append(f"Me: {chat_input}")
                    chat_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    chat_input = chat_input[:-1]
                else:
                    chat_input += event.unicode

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    start_client()
