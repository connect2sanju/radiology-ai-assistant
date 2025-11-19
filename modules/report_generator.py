import base64
from io import BytesIO
from typing import Optional, Callable

from PIL import Image


def encode_image(image: Image.Image, max_size: int = 512) -> str:
    """
    Convert PIL Image to a resized base64 string for OpenAI vision models.
    """
    width, height = image.size
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=80, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def generate_radiology_report(
    image: Image.Image,
    api_key: str,
    model_name: str = "gpt-4o",
    temperature: float = 0.2,
    max_tokens: int = 1024,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Generate a structured radiology report using an OpenAI GPT model with vision support.
    """
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required to generate a radiology report.")

    try:
        from openai import OpenAI, OpenAIError, RateLimitError
    except ImportError as exc:
        raise ImportError("OpenAI library not installed. Run: pip install openai") from exc

    img_b64 = encode_image(image)
    client = OpenAI(api_key=api_key)

    if progress_callback:
        progress_callback("Generating report with OpenAI GPT model...")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior radiologist. Generate a structured report with "
                        "Findings, Impression, and Recommendation sections."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ],
                },
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except RateLimitError as e:
        raise RuntimeError(
            "OpenAI API reported 'insufficient_quota' or rate limiting. "
            "Please check your OpenAI plan/billing status or wait before retrying."
        ) from e
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {e}") from e

    return response.choices[0].message.content.strip()
