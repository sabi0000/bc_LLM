import json
import time
from pathlib import Path

from ollama import chat


MODEL = "llama3.2"
STABLE_THRESHOLD_PERCENT = 1.0


def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_expected_trends(data):
    if len(data) < 2:
        raise ValueError("Na vyhodnotenie su potrebne aspon 2 casove body.")

    first = data[0]
    last = data[-1]

    expected = {}

    for variable in first:
        if variable == "Time_s":
            continue

        initial = first.get(variable)
        final = last.get(variable)

        if not isinstance(initial, (int, float)):
            continue

        if not isinstance(final, (int, float)):
            continue

        if initial == 0:
            if final > initial:
                trend = "increase"
            elif final < initial:
                trend = "decrease"
            else:
                trend = "stable"

            percent_change = None

        else:
            percent_change = ((final - initial) / abs(initial)) * 100

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


def build_prompt(data, variables, strategy):
    data_text = json.dumps(data, indent=2, ensure_ascii=False)

    variable_text = "\n".join(
        f"- {variable}"
        for variable in variables
    )

    # Toto musi byt rovnake pre P1, P2 aj P3,
    # aby vsetky modely pouzivali rovnake pravidlo pre trend.
    trend_rules = f"""
TREND CLASSIFICATION RULE:

- stable: absolute percentage change is less than {STABLE_THRESHOLD_PERCENT} %
- increase: percentage change is greater than or equal to {STABLE_THRESHOLD_PERCENT} %
- decrease: percentage change is less than or equal to -{STABLE_THRESHOLD_PERCENT} %

Calculate percentage change as:

((final - initial) / abs(initial)) * 100
"""

    # Aj vystupny format musi byt rovnaky,
    # aby sa dali vysledky automaticky porovnavat.
    output_format = """
Return ONLY valid JSON in this structure:

{
  "trends": {
    "VARIABLE_NAME": "increase"
  },
  "summary": "...",
  "interpretation": "...",
  "limitations": [
    "..."
  ]
}

Allowed trend values:
increase
decrease
stable
"""

    if strategy == "P1":
        instructions = """
Analyze the physiological data.

Determine whether each listed variable increased,
decreased or remained stable.

Provide a short interpretation.
"""

    elif strategy == "P2":
        instructions = """
Analyze the physiological data systematically.

Tasks:

1. Determine the change of every listed variable
   between the first and last measurement.
2. Classify every trend as increase, decrease or stable.
3. Summarize the most important observations.
4. Provide a possible physiological interpretation.
5. Describe limitations of the available data.
"""

    elif strategy == "P3":
        instructions = """
Analyze the physiological data systematically.

Tasks:

1. Determine the change of every listed variable
   between the first and last measurement.
2. Classify every trend as increase, decrease or stable.
3. Summarize the most important observations.
4. Provide a possible physiological interpretation.
5. Describe limitations of the available data.

IMPORTANT RULES:

- Use only information contained in the supplied data.
- Do not invent measurements.
- Do not invent symptoms.
- Do not invent diagnoses.
- Do not invent causes of the physiological changes.
- Do not invent treatments or interventions.
- Do not assume any patient information.
- Do not assume the name of the simulation.
- Clearly distinguish observations from interpretations.
- If a conclusion cannot be supported by the supplied data,
  explicitly state that it cannot be determined.
"""

    else:
        raise ValueError(f"Neznama prompt strategy: {strategy}")

    return f"""
{instructions}

PHYSIOLOGICAL DATA:

{data_text}

VARIABLES:

{variable_text}

{trend_rules}

{output_format}
"""


def ask_llm(prompt):
    start = time.perf_counter()

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an assistant analyzing physiological simulation data."
            },
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

    elapsed = time.perf_counter() - start

    result = json.loads(response.message.content)

    return result, elapsed


def evaluate_trends(expected, llm_result):
    llm_trends = llm_result.get("trends", {})

    comparison = {}
    correct = 0
    total = 0

    for variable, ground_truth in expected.items():
        expected_trend = ground_truth["expected_trend"]
        llm_trend = llm_trends.get(variable)

        is_correct = llm_trend == expected_trend

        comparison[variable] = {
            "expected": expected_trend,
            "llm": llm_trend,
            "correct": is_correct
        }

        total += 1

        if is_correct:
            correct += 1

    accuracy = (correct / total * 100) if total else 0.0

    return comparison, accuracy


def print_result(strategy, comparison, accuracy, response_time, llm_result):
    print("\n" + "=" * 70)
    print(f"PROMPT STRATEGY: {strategy}")
    print("=" * 70)

    for variable, result in comparison.items():
        symbol = "OK" if result["correct"] else "X"

        print(
            f"{variable:35} "
            f"expected: {result['expected']:10} "
            f"LLM: {str(result['llm']):10} "
            f"{symbol}"
        )

    print(f"\nTrend accuracy: {accuracy:.1f} %")
    print(f"Response time: {response_time:.2f} s")

    print("\nSummary:")
    print(llm_result.get("summary", ""))

    print("\nInterpretation:")
    print(llm_result.get("interpretation", ""))

    print("\nLimitations:")
    limitations = llm_result.get("limitations", [])

    if limitations:
        for limitation in limitations:
            print("-", limitation)
    else:
        print("- none returned")


def select_json_file():
    json_files = [
        file
        for file in Path(".").glob("*.json")
        if not file.name.startswith("evaluation_")
        and not file.name.startswith("prompt_comparison_")
    ]

    if not json_files:
        print("V aktualnom priecinku sa nenasli ziadne JSON subory.")
        return None

    json_files = sorted(json_files)

    print("\nDostupne simulacie:\n")

    for i, file in enumerate(json_files, start=1):
        print(f"{i}. {file.name}")

    try:
        choice = int(input("\nVyber cislo simulacie: "))
        return json_files[choice - 1]

    except (ValueError, IndexError):
        print("Neplatny vyber.")
        return None


def main():
    selected_file = select_json_file()

    if selected_file is None:
        return

    data = load_data(selected_file)

    if not isinstance(data, list):
        print("JSON musi obsahovat zoznam merani.")
        return

    print(f"\nNacitany subor: {selected_file.name}")
    print(f"Pocet zaznamov: {len(data)}")
    print(f"Model: {MODEL}")

    expected = calculate_expected_trends(data)
    variables = list(expected.keys())

    print("\nGround truth vypocitany Pythonom:\n")

    for variable, values in expected.items():
        percent_change = values["percent_change"]

        if percent_change is None:
            percent_text = "N/A"
        else:
            percent_text = f"{percent_change:.3f} %"

        print(
            f"{variable:35} "
            f"{values['initial']} -> {values['final']} | "
            f"{percent_text:12} | "
            f"{values['expected_trend']}"
        )

    strategies = ["P1", "P2", "P3"]
    all_results = []

    safe_model_name = MODEL.replace(":", "_")

    for strategy in strategies:
        prompt = build_prompt(
            data=data,
            variables=variables,
            strategy=strategy
        )

        print(f"\nSpustam {strategy}...")

        try:
            llm_result, response_time = ask_llm(prompt)

        except Exception as e:
            print(f"Chyba pri {strategy}: {e}")
            continue

        comparison, accuracy = evaluate_trends(
            expected=expected,
            llm_result=llm_result
        )

        print_result(
            strategy=strategy,
            comparison=comparison,
            accuracy=accuracy,
            response_time=response_time,
            llm_result=llm_result
        )

        output = {
            "dataset": selected_file.name,
            "model": MODEL,
            "prompt_strategy": strategy,
            "stable_threshold_percent": STABLE_THRESHOLD_PERCENT,
            "response_time_seconds": response_time,
            "trend_accuracy_percent": accuracy,
            "ground_truth": expected,
            "comparison": comparison,
            "llm_response": llm_result,
            "manual_evaluation": {
                "hallucination_control": None,
                "interpretation_quality": None,
                "limitations_handling": None,
                "relevance": None,
                "instruction_adherence": None
            }
        }

        output_file = (
            f"evaluation_{selected_file.stem}_"
            f"{safe_model_name}_{strategy}.json"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        all_results.append({
            "prompt_strategy": strategy,
            "trend_accuracy_percent": accuracy,
            "response_time_seconds": response_time,
            "output_file": output_file
        })

    comparison_file = (
        f"prompt_comparison_{selected_file.stem}_{safe_model_name}.json"
    )

    with open(comparison_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "dataset": selected_file.name,
                "model": MODEL,
                "results": all_results
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 70)
    print("FINALNE POROVNANIE")
    print("=" * 70)

    for result in all_results:
        print(
            f"{result['prompt_strategy']}: "
            f"accuracy = {result['trend_accuracy_percent']:.1f} %, "
            f"time = {result['response_time_seconds']:.2f} s"
        )

    print(f"\nSuhrn ulozeny do: {comparison_file}")


if __name__ == "__main__":
    main()
