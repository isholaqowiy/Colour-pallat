def calculate_grid_dimensions(count: int, canvas_width: int, canvas_height: int) -> list:
    """Calculates specific grid matrix coordinates depending on the total image count."""
    boxes = []
    if count <= 2:
        cols, rows = count, 1
    elif count <= 4:
        cols, rows = 2, 2
    elif count <= 6:
        cols, rows = 3, 2
    elif count <= 9:
        cols, rows = 3, 3
    else:
        cols, rows = 4, max(3, (count + 3) // 4)

    box_w = canvas_width // cols
    box_h = canvas_height // rows

    for r in range(rows):
        for c in range(cols):
            if len(boxes) < count:
                x1 = c * box_w
                y1 = r * box_h
                boxes.append((x1, y1, x1 + box_w, y1 + box_h))
    return boxes

