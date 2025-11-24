"""
Image Generation Module (Module C)

Generates kid-friendly illustrations using OpenAI DALL-E 3.
Falls back to placeholder images when API key is unavailable.
"""

import os
import base64
import io
from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    """Generates kid-friendly illustrations for academic paper concepts."""

    def __init__(self, backend="placeholder"):
        """
        Initialize image generator.

        Args:
            backend: "placeholder" or "openai"
        """
        self.backend = backend
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def generate_images(self, key_points, style="pastel", max_images=5):
        """
        Generate images for given key points.

        Args:
            key_points: List of concepts to illustrate
            style: "pastel" | "colorful" | "simple"
            max_images: Maximum number of images (default: 5)

        Returns:
            List of image objects with url, description, key_point, backend
        """
        key_points = key_points[:max_images]
        images = []

        for i, point in enumerate(key_points):
            try:
                if self.backend == "openai" and self.openai_key:
                    img = self._gen_openai(point, style)
                else:
                    img = self._gen_placeholder(point, style, i)
                images.append(img)
            except Exception as e:
                print(f"Image generation failed for '{point}': {e}")
                images.append(self._gen_placeholder(point, style, i, error=True))

        return images

    def _gen_placeholder(self, point, style, idx, error=False):
        """Generate placeholder image with colored background and text."""
        colors = {
            "pastel": [("#FFB3BA", "#000"), ("#BAFFC9", "#000"), ("#BAE1FF", "#000"),
                      ("#FFFFBA", "#000"), ("#FFD9BA", "#000")],
            "colorful": [("#FF6B6B", "#FFF"), ("#4ECDC4", "#FFF"), ("#45B7D1", "#FFF"),
                        ("#FFA07A", "#FFF"), ("#98D8C8", "#FFF")],
            "simple": [("#E8E8E8", "#333"), ("#D0D0D0", "#333"), ("#C0C0C0", "#333")]
        }

        palette = colors.get(style, colors["pastel"])
        bg, fg = palette[idx % len(palette)]

        # Create image
        img = Image.new('RGB', (512, 512), bg)
        draw = ImageDraw.Draw(img)

        # Load fonts
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except:
            font = small = ImageFont.load_default()

        # Word wrap text
        words = point.split()
        lines, current = [], []
        for word in words:
            current.append(word)
            if draw.textbbox((0, 0), ' '.join(current), font=font)[2] > 452:
                current.pop()
                if current:
                    lines.append(' '.join(current))
                current = [word]
        if current:
            lines.append(' '.join(current))

        # Draw centered text
        y = (512 - len(lines) * 40) // 2
        for line in lines:
            w = draw.textbbox((0, 0), line, font=font)[2]
            draw.text(((512 - w) // 2, y), line, fill=fg, font=font)
            y += 45

        # Add watermark
        draw.text((10, 484), "PaperBuddy", fill=fg, font=small)

        # Convert to base64
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()

        return {
            "url": f"data:image/png;base64,{b64}",
            "description": point,
            "key_point": point,
            "backend": "placeholder"
        }

    def _gen_openai(self, point, style):
        """Generate image using OpenAI DALL-E 3."""
        import openai

        prompt = self._build_prompt(point, style)
        client = openai.OpenAI(api_key=self.openai_key)

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        return {
            "url": response.data[0].url,
            "description": point,
            "key_point": point,
            "backend": "openai"
        }

    def _build_prompt(self, point, style):
        """Build kid-friendly DALL-E prompt."""
        styles = {
            "pastel": "soft pastel colors, gentle, dreamy",
            "colorful": "bright vibrant colors, cheerful",
            "simple": "minimalist, clean, simple"
        }
        style_desc = styles.get(style, styles["pastel"])

        return (
            f"A kid-friendly educational illustration showing: {point}. "
            f"Style: {style_desc}, children's book aesthetic, "
            f"cute, simple, clear concept, suitable for 5-year-olds, high quality"
        )
