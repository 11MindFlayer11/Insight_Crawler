import os
from openai import OpenAI
import json
from pydantic import BaseModel


# --- Summarization Functions ---
def summarize_content(content: str) -> dict:
    """Summarize content using OpenAI with chunking"""

    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.github.ai/inference"

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    class AnalysisRequest(BaseModel):
        url: str

    MAX_TOKENS = 12000  # Adjust based on model limits

    # Chunk content if too long
    chunks = [content[i : i + MAX_TOKENS] for i in range(0, len(content), MAX_TOKENS)]

    summaries = []
    for chunk in chunks:
        response = client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Analyze this content and return JSON with:
                - "offerings": 2-sentence summary of company offerings
                - "channels": Top 3 marketing channels (like youtube, linkedin, etc) based on the product type - as comma-separated string
                - "blog_titles": Generate 3 SEO-optimized blog titles for a company - as comma-separated string""",
                },
                {"role": "user", "content": chunk},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        summaries.append(json.loads(response.choices[0].message.content))

    # Combine summaries
    final_summary = {
        "offerings": " ".join([s["offerings"] for s in summaries]),
        "channels": ", ".join(
            list(
                set(
                    channel.strip()
                    for s in summaries
                    for channel in s["channels"].split(",")
                )
            )[:3]
        ),
        "blog_titles": ", ".join(
            list(
                set(
                    blog_title.strip()
                    for s in summaries
                    for blog_title in s["blog_titles"].split(",")
                )
            )[:3]
        ),
    }
    return final_summary
