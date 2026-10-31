# AI Usage, Debugging, and Limitations

## 1. AI Integration

This application uses Ollama with the locally hosted `qwen2.5-coder:3b` model to interpret natural-language business questions.

The model returns structured JSON containing an analytical intent and relevant parameters. The backend validates the intent against an allowlist and maps it to predefined Python analytics functions.

The LLM does not generate or directly execute SQL queries.

## 2. AI-Assisted Development

AI tools were used to assist with:
- Understanding FastAPI, Streamlit, SQLite, and Ollama integration.
- Debugging Python and SQL implementation issues.
- Improving code organization and validation.
- Designing and reviewing test cases.
- Preparing technical documentation.

AI-generated suggestions were reviewed, adapted, and tested.

## 3. Testing and Debugging

The application was tested for:
- CSV schema and data-quality validation.
- Repeated CSV loading.
- Revenue and aggregation calculations.
- Region and product filtering.
- Supported and unsupported AI questions.
- API response handling.

Automated tests can be executed using:

```bash
python -m pytest -v
```

## 4. Safety Measures

- Only predefined analytical intents are accepted.
- Unsupported or invalid intents are rejected.
- User-provided filters use parameterized SQL.
- The LLM does not have unrestricted database execution access.
- Destructive database operations are not exposed through the API.

## 5. Limitations

- The assistant supports a predefined set of analytical intents.
- The application currently uses one sales dataset.
- AI questions do not automatically inherit dashboard filters.
- Complex multi-step questions are not supported.
- The local model's response quality depends on the model and runtime.

## 6. Future Improvements

- Filter-aware natural-language analytics.
- Multi-turn conversational questions.
- Additional analytical operations and datasets.
- More integration and edge-case tests.
- Authentication and deployment support.
