"""
Image Generation Module (Module C)

Generates professional educational illustrations using OpenAI DALL-E 3.
Creates clear, informative visuals to explain academic concepts simply.
Falls back to placeholder images when API key is unavailable.
"""

import os
import base64
import io
from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    """Generates clear, professional illustrations for academic paper concepts."""

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
        # Intelligently select concepts that benefit most from visualization
        selected_points = self._select_visualizable_concepts(key_points, max_images)
        images = []

        for i, point in enumerate(selected_points):
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

    def _select_visualizable_concepts(self, key_points, max_images):
        """
        Select concepts that benefit most from visual explanation.
        Dynamically determines optimal number of images based on content quality.

        Prioritizes:
        - Process/workflow descriptions (how things work)
        - System architectures or structures
        - Comparisons and relationships
        - Complex mechanisms

        Deprioritizes:
        - Simple definitions
        - Pure statistics or numbers
        - Abstract conclusions
        """
        # Keywords that indicate good visualization candidates
        visual_keywords = [
            # Processes and mechanisms
            'process', 'mechanism', 'workflow', 'pipeline', 'system',
            'architecture', 'framework', 'structure', 'model',
            # Actions and transformations
            'how', 'works', 'transforms', 'converts', 'generates',
            'analyzes', 'processes', 'computes', 'calculates',
            # Relationships and comparisons
            'relationship', 'interaction', 'between', 'compared',
            'versus', 'difference', 'connection', 'flow',
            # Complex concepts
            'algorithm', 'method', 'approach', 'technique', 'strategy'
        ]

        # Keywords that indicate less visual concepts
        non_visual_keywords = [
            'results show', 'conclusion', 'found that', 'demonstrates',
            'percentage', 'number of', 'statistics', 'data shows',
            'proved', 'confirmed', 'validated'
        ]

        # Score each key point
        scored_points = []
        for point in key_points:
            point_lower = point.lower()

            # Calculate visual score
            visual_score = sum(1 for kw in visual_keywords if kw in point_lower)
            non_visual_penalty = sum(1 for kw in non_visual_keywords if kw in point_lower)

            # Longer, more detailed points are often better for visualization
            length_bonus = min(len(point.split()) / 20, 1.0)

            final_score = visual_score - non_visual_penalty + length_bonus
            scored_points.append((final_score, point))

        # Sort by score (descending)
        scored_points.sort(reverse=True, key=lambda x: x[0])

        # Dynamic selection: only include concepts with score > threshold
        # This ensures we only generate images for truly visual concepts
        SCORE_THRESHOLD = 0.5  # Minimum score to be worth visualizing

        worthy_points = [
            (score, point) for score, point in scored_points
            if score >= SCORE_THRESHOLD
        ]

        # Determine optimal number of images based on quality
        if not worthy_points:
            # No concepts meet the threshold - maybe generate 1-2 placeholders
            num_to_select = min(2, len(key_points))
            selected = [point for _, point in scored_points[:num_to_select]]
        else:
            # Select based on quality: more high-quality concepts = more images
            # But cap at max_images
            num_to_select = min(len(worthy_points), max_images)

            # Further reduce if scores are low overall
            avg_score = sum(score for score, _ in worthy_points[:num_to_select]) / num_to_select

            if avg_score < 1.0:
                # Low average score - reduce number
                num_to_select = max(1, num_to_select // 2)
            elif avg_score > 2.0:
                # High average score - use more images (up to max)
                num_to_select = min(num_to_select, max_images)

            selected = [point for _, point in worthy_points[:num_to_select]]

        # Maintain original order for consistency
        result = [p for p in key_points if p in selected]

        print(f"Selected {len(result)} out of {len(key_points)} concepts for visualization")
        return result

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
        """Build professional educational DALL-E prompt."""
        styles = {
            "pastel": "soft pastel colors, gentle, professional",
            "colorful": "bright vibrant colors, engaging, modern",
            "simple": "minimalist, clean, professional"
        }
        style_desc = styles.get(style, styles["pastel"])

        return (
            f"A clear, professional educational illustration showing: {point}. "
            f"Style: {style_desc}, scientific illustration style, "
            f"clean design, easy to understand, informative, high quality, "
            f"suitable for academic presentation"
        )
