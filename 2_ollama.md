# OLLAMA
https://ollama.com/

Kontrola:

`ollama --version`

`ollama version is 0.19.0`

`ollama list`

`NAME    ID    SIZE    MODIFIED`


Stiahnutie modelu:

`ollama run llama3.2`


Test modelu:

```
>>>
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
Based on the provided data, the following physiological changes can be observed:

1. Increased heart rate: The initial heart rate is 72 bpm, and the final heart rate is 118 bpm, indicating an
increase of 46 bpm.
2. Decreased systolic arterial pressure: The initial systolic arterial pressure is 120 mmHg, and the final
systolic arterial pressure is 85 mmHg, indicating a decrease of 35 mmHg.

It is not possible to draw any conclusions about changes in diastolic blood pressure or other physiological
parameters based on the provided data.
>>> /bye

```

Test API:
http://localhost:11434/api/version

`{"version":"0.19.0"}`

VS CODE:

`pip install ollama`


Vytvoríme test súbor:
[Test súbor](llm/test_ollama.py)

Pridame [JSON](llm/simulation_summary.json)

Napiseme skript pre LLM a vstup dat z json
[SKRIPT](llm/priklad1.py)

Vypis:
```
--- LLM REPORT ---

Physiological Report

**Main Observations**

- The heart rate increased from 72 beats per minute (initial) to 118 beats per minute (final), with a range of 72-118 beats per minute and a mean value of 91.2 beats per minute.

- Systolic arterial pressure decreased from 120 millimeters of mercury (initial) to 85 millimeters of mercury (final), with a range of 85-120 millimeters of mercury and a mean value of 103.4 millimeters of mercury.

**Important Changes**

- The heart rate shows a significant increase, indicating possible stress or exertion.
- Systolic arterial pressure exhibits a notable decrease.

**Possible Interpretation**

The observed changes in heart rate and systolic arterial pressure might suggest an acute physiological response to physical activity or stress. The elevated heart rate could be compensating for the decreased blood pressure to maintain adequate circulation.

**Limitations of the Available Data**

- There is no information available on diastolic arterial pressure, which could provide further insights into cardiovascular health.
- Changes in respiratory rate, body temperature, or other vital signs are not reported, making it difficult to draw a comprehensive picture of the individual's physiological state during this period.
```