from openai import AzureOpenAI
from config.config import OPENAI_API_KEY
from config.config import AZURE_ENDPOINT
from config.config import API_VERSION

client = AzureOpenAI(api_key=OPENAI_API_KEY, azure_endpoint=AZURE_ENDPOINT, api_version=API_VERSION)

def generate_testcases(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You generate high-quality QA test cases."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
