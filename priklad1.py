import json
from ollama import chat


# 1. Nacitanie dat
with open("simulation_summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# 2. Prompt builder
prompt = f"""
You are analyzing physiological data produced by a simulation.

Simulation data:

{json.dumps(data, indent=2)}

Generate a short physiological report.

Rules:
- Use only information contained in the provided data.
- Do not invent missing measurements.
- Clearly distinguish observations from interpretations.
- Do not make a diagnosis unless it is directly supported by the provided data.
- If information is insufficient, explicitly state this.

Structure your response as:

1. Main observations
2. Important changes
3. Possible interpretation
4. Limitations of the available data
"""


# 3. Local LLM
response = chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)


# 4. Report
print("\n--- LLM REPORT ---\n")
print(response.message.content)