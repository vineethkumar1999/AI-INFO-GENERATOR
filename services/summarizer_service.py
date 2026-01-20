from openai import AzureOpenAI
from config.config import OPENAI_API_KEY
from config.config import AZURE_ENDPOINT
from config.config import API_VERSION

client = AzureOpenAI(api_key=OPENAI_API_KEY, azure_endpoint=AZURE_ENDPOINT, api_version=API_VERSION)

def generate_summary(text):
    prompt = f"""
You are an expert QA engineer.
Summarize the following content in a structured, detailed way.Summarize the following content clearly and concisely.
Focus on reusable technical knowledge.
Focus on:
- Functional behavior
- Edge cases
- Constraints
- Inputs and outputs

Content:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You summarize product documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content
