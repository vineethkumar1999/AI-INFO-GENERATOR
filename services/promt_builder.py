def build_testcase_prompt(summaries, user_query):
    context = "\n\n---\n\n".join(summaries)

    prompt = f"""
You are a senior QA engineer and product expert. Keep the discussion with respect to the product and the context provided and question asked.

Below is the product knowledge context:
{context}

Based on the above context, do the following:
{user_query}

Generate:
- Functional Description and Behavior in detail


Format clearly and professionally.
"""

    return prompt
