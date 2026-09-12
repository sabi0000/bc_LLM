from ollama import chat

response = chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": """
You are analyzing physiological data from a simulation.

Heart rate:
initial: 72 bpm
final: 118 bpm

Systolic arterial pressure:
initial: 120 mmHg
final: 85 mmHg

Describe the observed physiological changes.

Rules:
- Use only the provided data.
- Do not invent missing values.
- Do not assume a diagnosis.
- If a conclusion cannot be supported by the data, explicitly state that.
"""
        }
    ]
)

print(response.message.content)