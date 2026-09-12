import json
import time
from pathlib import Path

from ollama import chat


MODEL = "llama3.2"

# Pilotne:
# zmenu mensiu ako 1 % budeme povazovat za stabilnu.
# Pre bakalarku sa toto neskor metodicky upravi.
STABLE_THRESHOLD_PERCENT = 1.0


# ============================================================
# LOAD DATA
# ============================================================

def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# GROUND TRUTH - TRENDY VYPOCITANE PYTHONOM
# ============================================================

def calculate_expected_trends(data):

    if len(data) < 2:
        raise ValueError("Na vyhodnotenie potrebujeme aspon 2 casove body.")

    first = data[0]
    last = data[-1]

    expected = {}

    for variable in first:

        # Cas nechceme hodnotit ako fyziologicku velicinu
        if variable == "Time_s":
            continue

        initial = first.get(variable)
        final = last.get(variable)

        if not isinstance(initial, (int, float)):
            continue

        if not isinstance(final, (int, float)):
            continue

        difference = final - initial

        # ochrana proti deleniu nulou
        if initial == 0:

            if difference > 0:
                trend = "increase"
            elif difference < 0:
                trend = "decrease"
            else:
                trend = "stable"

            percent_change = None

        else:

            percent_change = (difference / abs(initial)) * 100

            if abs(percent_change) < STABLE_THRESHOLD_PERCENT:
                trend = "stable"

            elif percent_change > 0:
                trend = "increase"

            else:
                trend = "decrease"

        expected[variable] = {
            "initial": initial,
            "final": final,
            "percent_change": percent_change,
            "expected_trend": trend
        }

    return expected


# ============================================================
# EVALUATION PROMPT
# ============================================================

def build_evaluation_prompt(data, variables):

    data_text = json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    )

    variable_text = "\n".join(
        f"- {variable}"
        for variable in variables
    )

    return f"""
You are analyzing physiological simulation data.

Use ONLY the supplied measurements.

Do not invent measurements, symptoms, diagnoses,
patient information, causes, treatments or events that
are not contained in the data.

DATA:

{data_text}


Evaluate the change from the FIRST measurement
to the LAST measurement.

For every variable listed below classify its trend as:

increase
decrease
stable


Variables:

{variable_text}


Then provide:
- a short summary of the most important observations
- a cautious possible physiological interpretation
- limitations of the available data

Do not attempt to identify the name of the simulation.

Return ONLY valid JSON in this exact general structure:

{{
    "trends": {{
        "VARIABLE_NAME": "increase"
    }},
    "summary": "...",
    "interpretation": "...",
    "limitations": [
        "..."
    ]
}}

The only allowed trend values are:

increase
decrease
stable
"""

f"""
Classify the change using this exact rule:

- stable: absolute percentage change is less than {STABLE_THRESHOLD_PERCENT} %
- increase: percentage change is greater than or equal to {STABLE_THRESHOLD_PERCENT} %
- decrease: percentage change is less than or equal to -{STABLE_THRESHOLD_PERCENT} %

Calculate the percentage change as:

((final - initial) / abs(initial)) * 100
"""


# ============================================================
# LLM
# ============================================================

def ask_llm_evaluation(prompt):

    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are a cautious assistant for analyzing
simulated physiological data.

Base all statements only on supplied data.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        # chceme strojovo citatelnu odpoved
        format="json",

        # pre porovnavanie modelov chceme co najmensiu nahodnost
        options={
            "temperature": 0
        }
    )

    end = time.perf_counter()

    answer_text = response.message.content

    result = json.loads(answer_text)

    response_time = end - start

    return result, response_time


# ============================================================
# AUTOMATIC SCORING
# ============================================================

def evaluate_trends(expected, llm_result):

    llm_trends = llm_result.get("trends", {})

    results = {}

    correct = 0
    total = 0

    for variable, ground_truth in expected.items():

        expected_trend = ground_truth["expected_trend"]

        llm_trend = llm_trends.get(variable)

        is_correct = llm_trend == expected_trend

        results[variable] = {
            "expected": expected_trend,
            "llm": llm_trend,
            "correct": is_correct
        }

        total += 1

        if is_correct:
            correct += 1

    if total > 0:
        accuracy = correct / total * 100
    else:
        accuracy = 0

    return results, accuracy


# ============================================================
# EVALUATION MODE
# ============================================================

def evaluation_mode(data, selected_file):

    print("\n========================================")
    print("EVALUATION MODE")
    print("========================================")

    expected = calculate_expected_trends(data)

    variables = list(expected.keys())

    print("\nPython vypocital ground truth:\n")

    for variable, values in expected.items():

        print(
            f"{variable}: "
            f"{values['initial']} -> "
            f"{values['final']} "
            f"= {values['expected_trend']}"
        )

    prompt = build_evaluation_prompt(
        data,
        variables
    )

    print(f"\nPosielam data modelu {MODEL}...\n")

    try:
        llm_result, response_time = ask_llm_evaluation(prompt)

    except Exception as e:
        print("Chyba pri komunikacii s LLM:")
        print(e)
        return

    comparison, accuracy = evaluate_trends(
        expected,
        llm_result
    )

    print("\n========================================")
    print("POROVNANIE TRENDOV")
    print("========================================\n")

    for variable, result in comparison.items():

        symbol = "OK" if result["correct"] else "X"

        print(
            f"{variable:35} "
            f"expected: {result['expected']:10} "
            f"LLM: {str(result['llm']):10} "
            f"{symbol}"
        )

    print("\n----------------------------------------")

    print(
        f"Trend accuracy: {accuracy:.1f} %"
    )

    print(
        f"Response time: {response_time:.2f} s"
    )

    print("\n========================================")
    print("LLM SUMMARY")
    print("========================================")

    print(
        llm_result.get(
            "summary",
            "No summary returned."
        )
    )

    print("\n========================================")
    print("LLM INTERPRETATION")
    print("========================================")

    print(
        llm_result.get(
            "interpretation",
            "No interpretation returned."
        )
    )

    print("\n========================================")
    print("LIMITATIONS")
    print("========================================")

    for limitation in llm_result.get("limitations", []):
        print("-", limitation)

    # ================================================
    # SAVE RESULT
    # ================================================

    safe_model_name = MODEL.replace(":", "_")

    output_file = (
        f"evaluation_"
        f"{selected_file.stem}_"
        f"{safe_model_name}.json"
    )

    output = {
        "dataset": selected_file.name,
        "model": MODEL,
        "stable_threshold_percent": STABLE_THRESHOLD_PERCENT,
        "response_time_seconds": response_time,
        "trend_accuracy_percent": accuracy,

        "ground_truth": expected,

        "comparison": comparison,

        "llm_response": llm_result,

        # tieto polia zatial vyplni hodnotitel rucne
        "manual_evaluation": {
            "hallucination_control": None,
            "interpretation_quality": None,
            "limitations_handling": None,
            "relevance": None,
            "instruction_adherence": None
        }
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nVysledok ulozeny do: {output_file}"
    )


# ============================================================
# CHAT MODE
# ============================================================

def chat_mode(data):

    data_text = json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    )

    messages = [
        {
            "role": "system",
            "content": """
You are analyzing physiological simulation data.

Rules:

- Use only supplied data.
- Do not invent measurements.
- Do not invent symptoms.
- Do not assume the cause of the simulation.
- Distinguish observations from interpretation.
- Explicitly state when information is insufficient.
"""
        },
        {
            "role": "user",
            "content": f"""
Use the following physiological data
as context for this conversation:

{data_text}
"""
        }
    ]

    print("\nChat pripraveny.")
    print("Pre ukoncenie napis: exit\n")

    while True:

        question = input("Ty: ")

        if question.lower() in [
            "exit",
            "quit",
            "koniec"
        ]:
            break

        messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        response = chat(
            model=MODEL,
            messages=messages
        )

        answer = response.message.content

        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        print("\nLLM:")
        print(answer)
        print()


# ============================================================
# MAIN
# ============================================================

def main():

    # nech sa nam vysledky evaluation nezobrazuju
    # ako vstupne simulacie
    json_files = [
        file
        for file in Path(".").glob("*.json")
        if not file.name.startswith("evaluation_")
    ]

    if not json_files:
        print("Nenasli sa JSON subory.")
        return

    print("\nDostupne simulacie:\n")

    for i, file in enumerate(
        json_files,
        start=1
    ):
        print(
            f"{i}. {file.name}"
        )

    try:

        choice = int(
            input(
                "\nVyber cislo simulacie: "
            )
        )

        selected_file = json_files[
            choice - 1
        ]

    except (ValueError, IndexError):

        print("Neplatny vyber.")
        return

    data = load_data(
        selected_file
    )

    print(
        f"\nNacitany subor: "
        f"{selected_file.name}"
    )

    print(
        f"Pocet zaznamov: "
        f"{len(data)}"
    )

    print("\nRezim:\n")

    print(
        "1 - Chat s datami"
    )

    print(
        "2 - Evaluation"
    )

    mode = input(
        "\nVyber rezim: "
    )

    if mode == "1":

        chat_mode(
            data
        )

    elif mode == "2":

        evaluation_mode(
            data,
            selected_file
        )

    else:

        print(
            "Neznamy rezim."
        )


if __name__ == "__main__":
    main()