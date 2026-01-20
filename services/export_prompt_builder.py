def build_export_testcase_prompt(summaries, user_query):
    context = "\n\n---\n\n".join(summaries)

    prompt = f"""
You are a senior QA engineer.

Below is the product knowledge context:
{context}

Task:
{user_query}

Generate test cases STRICTLY in JSON.
Do NOT include any explanation or text outside JSON.

Schema:
{{
  "test_cases": [
    {{
      "id": "TC_001",
      "title": "",
      "preconditions": "",
      "steps": ["step 1", "step 2"],
      "expected_result": "",
      "type": "Functional | Edge | Negative"
    }}
  ]
}}
"""

    return prompt
