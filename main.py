import numpy as np
import pygame
import math

width, height = 800, 600
background_color = (10, 10, 10)
surface_color = (0, 200, 255)

def get_projection_matrix(fov, aspect, near, far):
    f = 1 / math.tan(math.radians(fov) / 2)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ])

def apply_transform(point, matrix):
    point_h = np.array([*point, 1.0])
    transformed = matrix @ point_h
    return transformed[:3]

def project_point(point, projection_matrix):
    point_homogeneous = np.array([*point, 1.0])
    projected = projection_matrix @ point_homogeneous
    if projected[3] != 0:
        projected /= projected[3]
    x = int((projected[0] + 1) * width / 2)
    y = int((1 - projected[1]) * height / 2)
    return (x, y)

def get_rotation_matrix_y(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [ c, 0,  s, 0],
        [ 0, 1,  0, 0],
        [-s, 0,  c, 0],
        [ 0, 0,  0, 1]
    ])

def get_translation_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])

def generate_surface(alpha=2.0, beta=0.5, u_steps=50, v_steps=50):
    u_vals = np.linspace(0, 4 * np.pi, u_steps)
    v_vals = np.linspace(0, 2 * np.pi, v_steps)
    points = []
    for i in range(u_steps):
        row = []
        for j in range(v_steps):
            u = u_vals[i]
            v = v_vals[j]
            x = (alpha + beta * np.cos(v)) * np.cos(u)
            y = (alpha + beta * np.cos(v)) * np.sin(u)
            z = beta * np.sin(v) + alpha * u
            row.append((x, y, z))
        points.append(row)
    return points

def build_triangles(grid):
    triangles = []
    for i in range(len(grid) - 1):
        for j in range(len(grid[0]) - 1):
            p1 = grid[i][j]
            p2 = grid[i + 1][j]
            p3 = grid[i][j + 1]
            p4 = grid[i + 1][j + 1]
            triangles.append((p1, p2, p3))
            triangles.append((p2, p4, p3))
    return triangles

def draw_scene(screen, triangles, projection_matrix, transform_matrix):
    z_ordered = sorted(triangles, key=lambda tri: sum(apply_transform(p, transform_matrix)[2] for p in tri) / 3.0, reverse=True)
    for tri in z_ordered:
        transformed = [apply_transform(p, transform_matrix) for p in tri]
        proj = [project_point(p, projection_matrix) for p in transformed]
        pygame.draw.polygon(screen, surface_color, proj)

def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    proj_matrix = get_projection_matrix(fov=90, aspect=width / height, near=0.1, far=1000)
    grid = generate_surface()
    triangles = build_triangles(grid)

    angle_x = 0
    angle_y = 0
    running = True

    while running:
        screen.fill(background_color)

        rotate_y = get_rotation_matrix_y(angle_y)
        rotate_x = np.array([
            [1, 0, 0, 0],
            [0, np.cos(angle_x), -np.sin(angle_x), 0],
            [0, np.sin(angle_x), np.cos(angle_x), 0],
            [0, 0, 0, 1]
        ])
        rotation = rotate_x @ rotate_y
        translation = get_translation_matrix(0, 0, -30)
        transform_matrix = translation @ rotation

        draw_scene(screen, triangles, proj_matrix, transform_matrix)
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            angle_y -= 0.05
        if keys[pygame.K_RIGHT]:
            angle_y += 0.05
        if keys[pygame.K_UP]:
            angle_x -= 0.05
        if keys[pygame.K_DOWN]:
            angle_x += 0.05

if __name__ == "__main__":
    main()
