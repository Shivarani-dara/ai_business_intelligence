from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.database import validate_csv

from backend.analytics import (
    get_total_revenue,
    get_top_product,
    get_monthly_revenue,
    get_top_region,
    compare_months,
    get_dashboard_data
)

from backend.ai_interpreter import interpret_question


app = FastAPI(
    title="AI Business Intelligence Assistant",
    description="Natural language sales analytics API",
    version="1.0"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "AI Business Intelligence Assistant is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/analytics/revenue")
def total_revenue():
    result = get_total_revenue()

    return {
        "success": True,
        "answer": f"Total revenue is {result}",
        "supporting_data": {
            "total_revenue": result
        }
    }


@app.get("/analytics/top-product")
def top_product():
    product, revenue = get_top_product()

    return {
        "success": True,
        "answer": f"{product} generated the highest revenue",
        "supporting_data": {
            "product": product,
            "revenue": revenue
        }
    }


@app.get("/analytics/top-region")
def top_region():
    region, revenue = get_top_region()

    return {
        "success": True,
        "answer": f"{region} generated the highest revenue",
        "supporting_data": {
            "region": region,
            "revenue": revenue
        }
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        return {
            "success": False,
            "answer": "Please enter a question.",
            "supporting_data": {}
        }

    # Step 1: Ask the LLM to interpret the question
    try:
        interpretation = interpret_question(question)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI interpreter is unavailable. Please try again."
        )

    intent = interpretation["intent"]

    # Step 2: Execute the corresponding trusted analytics function

    if intent == "total_revenue":

        result = get_total_revenue()

        return {
            "success": True,
            "question": question,
            "answer": f"Total revenue is {result}",
            "supporting_data": {
                "total_revenue": result
            }
        }

    elif intent == "top_product":

        product, revenue = get_top_product()

        return {
            "success": True,
            "question": question,
            "answer": f"{product} generated the highest revenue",
            "supporting_data": {
                "product": product,
                "revenue": revenue
            }
        }

    elif intent == "monthly_revenue":

        results = get_monthly_revenue()

        monthly_data = [
            {
                "month": month,
                "revenue": revenue
            }
            for month, revenue in results
        ]

        return {
            "success": True,
            "question": question,
            "answer": "Here is the monthly revenue breakdown.",
            "supporting_data": {
                "monthly_revenue": monthly_data
            }
        }

    elif intent == "top_region":

        region, revenue = get_top_region()

        return {
            "success": True,
            "question": question,
            "answer": f"{region} generated the highest revenue",
            "supporting_data": {
                "region": region,
                "revenue": revenue
            }
        }

    elif intent == "compare_months":

        month1 = interpretation["month1"]
        month2 = interpretation["month2"]

        result = compare_months(month1, month2)

        return {
            "success": True,
            "question": question,
            "answer": (
                f"Revenue changed by "
                f"{result['difference']} between "
                f"{month1} and {month2}."
            ),
            "supporting_data": result
        }

    else:

        return {
            "success": False,
            "question": question,
            "answer": interpretation.get(
                "message",
                "Sorry, I cannot answer that question."
            ),
            "supporting_data": {}
        }


@app.get("/data-quality")
def data_quality():
    report = validate_csv()

    return {
        "success": True,
        "validation_report": report
    }

@app.get("/dashboard")
def dashboard(
    region: str | None = None,
    product: str | None = None
):
    try:
        data = get_dashboard_data(
            region=region,
            product=product
        )

        return {
            "success": True,
            "dashboard": data
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve dashboard analytics."
        )