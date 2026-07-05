import os
from PIL import Image, ImageOps
from config import TEMP_DIR
import layouts

def build_collage(image_paths: list, user_id: int, style: str = "Grid") -> str:
    """Resizes, crops, and stitches multiple source image files into a cohesive unified collage asset."""
    try:
        canvas_w, canvas_h = 1200, 1200
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))
        
        count = len(image_paths)
        boxes = layouts.calculate_grid_dimensions(count, canvas_w, canvas_h)

        for idx, path in enumerate(image_paths):
            if idx >= len(boxes):
                break
            with Image.open(path) as img:
                box = boxes[idx]
                target_w = box[2] - box[0]
                target_h = box[3] - box[1]
                
                # Center-crop image layout vectors to match target boxes aspect boundaries cleanly
                cropped_img = ImageOps.fit(img, (target_w, target_h), Image.Resampling.LANCZOS)
                canvas.paste(cropped_img, (box[0], box[1]))

        output_path = os.path.join(TEMP_DIR, f"collage_{user_id}.png")
        canvas.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Collage Processing Core Exception: {e}")
        return None

