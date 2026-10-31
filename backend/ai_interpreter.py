import json
import ollama


MODEL_NAME = "qwen2.5-coder:3b"

ALLOWED_INTENTS = {
    "total_revenue",
    "top_product",
    "monthly_revenue",
    "top_region",
    "compare_months",
    "unknown"
}

MONTHS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
    "01": "01",
    "02": "02",
    "03": "03",
    "04": "04",
    "05": "05",
    "06": "06",
    "07": "07",
    "08": "08",
    "09": "09",
    "10": "10",
    "11": "11",
    "12": "12"
}


def normalize_month(month):
    if not isinstance(month, str):
        return None

    return MONTHS.get(month.strip().lower())


def interpret_question(question):
    if not question or not question.strip():
        return {
            "intent": "unknown",
            "message": "Please enter a question."
        }

    prompt = f"""
You are an intent classifier for a sales analytics assistant.

Identify what the user wants and return ONLY valid JSON.

Allowed intents:

1. total_revenue
   Questions about total sales revenue.

2. top_product
   Questions about the product generating the highest revenue.

3. monthly_revenue
   Questions asking for revenue month by month.

4. top_region
   Questions about the region generating the highest revenue.

5. compare_months
   Questions comparing revenue between two months.
   Include month1 and month2 as full English month names.

6. unknown
   Questions unrelated to these analytics operations.

Examples:

Question: What is our total revenue?
Output: {{"intent": "total_revenue"}}

Question: Which product generated the most revenue?
Output: {{"intent": "top_product"}}

Question: Show monthly sales.
Output: {{"intent": "monthly_revenue"}}

Question: Which region performed best?
Output: {{"intent": "top_region"}}

Question: Compare January and February revenue.
Output: {{"intent": "compare_months", "month1": "January", "month2": "February"}}

Question: Tell me a joke.
Output: {{"intent": "unknown"}}

Rules:
- Never invent an intent.
- Never generate SQL.
- Return only JSON.
- For compare_months, include both months.

User question: {question}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json",
        options={
            "temperature": 0
        }
    )

    try:
        result = json.loads(response["message"]["content"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return {
            "intent": "unknown",
            "message": "Could not understand the question."
        }

    intent = result.get("intent")

    if intent not in ALLOWED_INTENTS:
        return {
            "intent": "unknown",
            "message": "Unsupported analytics request."
        }

    if intent == "compare_months":
        month1 = normalize_month(result.get("month1"))
        month2 = normalize_month(result.get("month2"))

        if not month1 or not month2:
            return {
                "intent": "unknown",
                "message": "Please specify two valid months."
            }

        return {
            "intent": intent,
            "month1": month1,
            "month2": month2
        }

    return {
        "intent": intent
    }