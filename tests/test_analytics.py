import pytest
from fastapi.testclient import TestClient

import backend.main as main

from backend.analytics import (
    get_total_revenue,
    get_top_product,
    get_monthly_revenue,
    get_top_region,
    compare_months
)

from backend.database import validate_csv


client = TestClient(main.app)


# Test 1: Total revenue calculation
def test_total_revenue():
    assert get_total_revenue() == 1439200.0


# Test 2: Highest revenue product
def test_top_product():
    product, revenue = get_top_product()

    assert product == "Monitor"
    assert revenue == 473000.0


# Test 3: Monthly revenue
def test_monthly_revenue():
    result = get_monthly_revenue()

    assert len(result) == 6
    assert result[0] == ("01", 210250.0)
    assert result[4] == ("05", 318500.0)


# Test 4: Highest revenue region
def test_top_region():
    region, revenue = get_top_region()

    assert region == "South"
    assert revenue == 411200.0


# Test 5: Month comparison
def test_compare_months():
    result = compare_months("01", "02")

    assert result["month1_revenue"] == 210250.0
    assert result["month2_revenue"] == 234600.0
    assert result["difference"] == 24350.0
    assert result["percentage_change"] == pytest.approx(11.58145)


# Test 6: CSV data validation
def test_csv_validation():
    report = validate_csv()

    assert report["schema_valid"] is True
    assert report["total_records"] == 51
    assert report["duplicate_transaction_ids"] == 0


# Test 7: Natural-language API
def test_ask_api(monkeypatch):
    monkeypatch.setattr(
        main,
        "interpret_question",
        lambda question: {"intent": "top_product"}
    )

    response = client.post(
        "/ask",
        json={
            "question": "Which product generated the highest revenue?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["supporting_data"]["product"] == "Monitor"


# Test 8: Unsupported question
def test_unsupported_question(monkeypatch):
    monkeypatch.setattr(
        main,
        "interpret_question",
        lambda question: {
            "intent": "unknown",
            "message": "Unsupported question"
        }
    )

    response = client.post(
        "/ask",
        json={"question": "Tell me a joke"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is False