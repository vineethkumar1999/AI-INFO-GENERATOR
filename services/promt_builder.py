def build_testcase_prompt(summaries, user_query):
    context = "\n\n---\n\n".join(summaries)

    prompt = f"""
You are a senior QA engineer.

Below is the product knowledge context:
{context}

Based on the above context, do the following:
{user_query}

Generate:
- Functional test cases
- Edge cases
- Negative scenarios
- Boundary conditions

Format clearly and professionally.
"""

    return prompt
