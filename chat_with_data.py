import json
from pathlib import Path
from ollama import chat


MODEL = "llama3.2"


# ---------------------------------------
# 1. Najdeme vsetky JSON subory
# ---------------------------------------

json_files = list(Path(".").glob("*.json"))

if not json_files:
    print("Nenasli sa ziadne JSON subory.")
    exit()


print("\nDostupne simulacie:\n")

for i, file in enumerate(json_files, start=1):
    print(f"{i}. {file.name}")


# ---------------------------------------
# 2. Pouzivatel vyberie data
# ---------------------------------------

choice = int(input("\nVyber cislo simulacie: "))

selected_file = json_files[choice - 1]


# ---------------------------------------
# 3. Nacitame JSON
# ---------------------------------------

with open(selected_file, "r", encoding="utf-8") as f:
    data = json.load(f)


data_text = json.dumps(
    data,
    indent=2,
    ensure_ascii=False
)


print(f"\nNacitane data zo suboru: {selected_file.name}")
print(f"Pocet zaznamov: {len(data)}")


# ---------------------------------------
# 4. Vytvorime zaciatok konverzacie
# ---------------------------------------

messages = [
    {
        "role": "system",
        "content": """
You are an assistant analyzing physiological simulation data.

Rules:
- Use only the physiological data provided to you.
- Do not invent measurements.
- Do not assume the cause or name of the simulation.
- Distinguish observations from interpretations.
- If the available data are insufficient to answer a question,
  explicitly say so.
- Values of OxygenSaturation are represented as fractions,
  e.g. 0.97 corresponds to approximately 97%.
"""
    },
    {
        "role": "user",
        "content": f"""
The following physiological measurements come from one simulation.

DATA:

{data_text}

Use these data as context for the following conversation.
Do not try to identify the simulation unless I explicitly ask you to interpret it.
"""
    }
]


# ---------------------------------------
# 5. Prva odpoved - iba potvrdenie
# ---------------------------------------

response = chat(
    model=MODEL,
    messages=messages
)

assistant_message = response.message.content

messages.append(
    {
        "role": "assistant",
        "content": assistant_message
    }
)

print("\nLLM:")
print(assistant_message)


# ---------------------------------------
# 6. Chat loop
# ---------------------------------------

print("\nMozes sa pytat na data.")
print("Pre ukoncenie napis: exit\n")


while True:

    question = input("Ty: ")

    if question.lower() in ["exit", "quit", "koniec"]:
        print("Konverzacia ukoncena.")
        break

    # pridame tvoju otazku do historie
    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # posleme celu konverzaciu Ollame
    response = chat(
        model=MODEL,
        messages=messages
    )

    answer = response.message.content

    # ulozime odpoved do historie
    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    print("\nLLM:")
    print(answer)
    print()