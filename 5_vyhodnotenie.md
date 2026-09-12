# VYHODNOCOVACIE SCENÁRE
## Vyhodnocovacie scenáre

| Skupina | Príklady | Čo sa testuje |
|---|---|---|
| Normálny stav | `baseline` / `normal` | či model nevymyslí patológiu |
| Jednoduchá odchýlka | tachykardia, hypotenzia, nízka SpO₂ | rozpoznanie jednej zmeny |
| Hemodynamická zmena | `hemorrhage` | trendy HR, MAP, CO, blood volume |
| Respiračný problém | `asthma` / `ARDS` / `airway obstruction` | SpO₂, RR a ich vývoj |
| Kardiovaskulárny stav | `pericardial`, `ventricular` / `arrhythmia` | kombinácia viacerých parametrov |
| Stres/záťaž | `acute stress`, `exercise` | fyziologická reakcia bez zbytočnej patologizácie |
| Kombinovaný stav | napr. hypotenzia + nízka SpO₂ | schopnosť sledovať viac zmien naraz |
| Chýbajúce údaje | odstránená SpO₂ alebo BP | či model prizná, že informácia chýba |
| Rušivé/neúplné dáta | menej časových bodov, prípadne chýbajúca hodnota | robustnosť |
| Hraničný prípad | veľmi malé zmeny | či model nepreháňa význam |

> **Každý model dostane presne rovnaké dáta a presne rovnaký prompt. Model nesmie vidieť názov súboru/scenára.**

### Príklad rovnakej otázky pre každý model

```text id="ed2g0l"
Analyze the physiological data.

Identify:
1. the most important observations,
2. changes over time,
3. possible physiological interpretation,
4. information that is insufficient or missing.

Use only the supplied data.
Do not invent measurements or clinical information.
```

## Hodnotiace kritériá

| Kritérium | Otázka |
|---|---|
| **Factual accuracy** | Sú tvrdenia v odpovedi podporené JSON dátami? |
| **Trend detection** | Správne zachytil rast, pokles alebo stabilitu hodnôt? |
| **Hallucination rate** | Vymyslel si hodnoty, symptómy, diagnózu alebo okolnosti, ktoré v dátach nie sú? |
| **Handling missing information** | Dokáže povedať „z týchto údajov to nemožno určiť“? |
| **Relevance** | Sústreďuje sa na podstatné zmeny alebo píše všeobecné informácie nesúvisiace priamo s dátami? |
| **Instruction adherence** | Dodržal požadovanú štruktúru a zákaz domýšľania? |

[Evaluovany model](llm/chat.py)

Vypis:
```
Rezim:

1 - Chat s datami
2 - Evaluation

Vyber rezim: 2

========================================
EVALUATION MODE
========================================

Python vypocital ground truth:

HeartRate_bpm: 84.0 -> 84.98 = increase
MeanArterialPressure_mmHg: 94.8 -> 94.75 = stable
CardiacOutput_L_min: 6.14 -> 6.02 = decrease
BloodVolume_mL: 5488.43 -> 5378.13 = decrease

Posielam data modelu llama3.2...


========================================
POROVNANIE TRENDOV
========================================

HeartRate_bpm                       expected: increase   LLM: decrease   X
MeanArterialPressure_mmHg           expected: stable     LLM: decrease   X
CardiacOutput_L_min                 expected: decrease   LLM: decrease   OK
BloodVolume_mL                      expected: decrease   LLM: decrease   OK

----------------------------------------
Trend accuracy: 50.0 %
Response time: 8.85 s

========================================
LLM SUMMARY
========================================
All measured variables show a decrease from the first to the last measurement.

========================================
LLM INTERPRETATION
========================================
The data suggests a general decline in physiological parameters over time. However, without additional context or information about the underlying cause of this trend, it is difficult to draw more specific conclusions.

========================================
LIMITATIONS
========================================
- Data only spans two time points, limiting the ability to identify trends or patterns over longer periods.

Vysledok ulozeny do: evaluation_hemorrhage_llama3.2.json
```
[evaluation_hemorrhage_llama3.2.json](llm/evaluation_hemorrhage_llama3.2.json)

## Pilotné vyhodnotenie – Llama 3.2 / `hemorrhage.json`

Pri testovaní modelu **Llama 3.2** na dátach zo scenára `hemorrhage.json` dosiahol model **presnosť identifikácie trendov 50 %**. Hodnotené boli štyri fyziologické veličiny.

| Parameter | Počiatočná hodnota | Konečná hodnota | Očakávaný trend | LLM | Výsledok |
|---|---:|---:|---|---|---|
| Heart rate | 84.00 bpm | 84.98 bpm | `increase` | `decrease` | ❌ |
| Mean arterial pressure | 94.80 mmHg | 94.75 mmHg | `stable` | `decrease` | ❌ |
| Cardiac output | 6.14 L/min | 6.02 L/min | `decrease` | `decrease` | ✅ |
| Blood volume | 5488.43 mL | 5378.13 mL | `decrease` | `decrease` | ✅ |

Pri **Mean Arterial Pressure** bola zmena približne **−0,05 %**, preto bola pri zvolenom prahu stability **1 %** klasifikovaná ako `stable`.

Model správne identifikoval **2 zo 4 trendov**.

Zaujímavé je najmä nesprávne vyhodnotenie srdcovej frekvencie. Hodnota numericky vzrástla:

```text
84.00 → 84.98 bpm
```

Model ju však označil ako pokles. Táto chyba sa následne preniesla aj do slovného zhrnutia, v ktorom model uviedol:

> All measured variables show a decrease from the first to the last measurement.

Toto tvrdenie je v rozpore so vstupnými dátami.

Na druhej strane model **nevymýšľal diagnózu, príčinu stavu, symptómy ani ďalšie neexistujúce údaje**. Jeho interpretácia bola pomerne opatrná a správne upozornil na obmedzenie dát – k dispozícii boli iba dva časové body.

**Čas generovania odpovede:** približne **8,85 s**

### Predbežný záver

Tento pilotný test ukazuje, že malý lokálny LLM nemusí byť spoľahlivý pri samotnom numerickom vyhodnocovaní zmien vo fyziologických dátach. Aj jednoduchú zmenu:

```text
84.00 → 84.98
```

dokázal interpretovať opačne.

To podporuje návrh architektúry, v ktorej by **numerický preprocessing vykonával Python** a LLM by dostával už vypočítané charakteristiky, napríklad:

- počiatočnú hodnotu,
- konečnú hodnotu,
- percentuálnu zmenu,
- trend.

Úlohou LLM by následne bola predovšetkým **interpretácia dát a vytvorenie textového reportu**, nie vykonávanie základných numerických výpočtov.

> Výsledok jedného scenára nestačí na hodnotenie kvality modelu ako celku. Rovnaký postup je potrebné zopakovať na viacerých scenároch a modeloch za rovnakých podmienok.

---

# Porovnanie promptovacích stratégií

Boli navrhnuté tri promptovacie stratégie:

| Stratégia | Popis |
|---|---|
| **P1** | jednoduchý prompt |
| **P2** | štruktúrovaný prompt |
| **P3** | štruktúrovaný prompt + explicitný zákaz halucinácií |

Experiment je implementovaný v skripte `evaluate_prompts.py`.

## Testovací scenár

```text
Vyber číslo simulácie: 1

Načítaný súbor: acute_stress.json
Počet záznamov: 2
Model: llama3.2
```

### Ground truth vypočítaný v Pythone

| Parameter | Počiatočná hodnota | Konečná hodnota | Zmena | Ground truth |
|---|---:|---:|---:|---|
| `HeartRate_bpm` | 83.999999999 | 85.942484767 | +2.312 % | `increase` |
| `ArterialPressure_mmHg` | 113.4494806258 | 117.9757384795 | +3.990 % | `increase` |
| `MeanArterialPressure_mmHg` | 94.7975690628 | 96.0632041061 | +1.335 % | `increase` |
| `SystolicPressure_mmHg` | 114.4655093908 | 118.0168403591 | +3.103 % | `increase` |
| `DiastolicPressure_mmHg` | 73.5177917102 | 72.3910738035 | −1.533 % | `decrease` |
| `OxygenSaturation` | 0.9727567053 | 0.9726344806 | −0.013 % | `stable` |
| `RespirationRate_bpm` | 16.0427807487 | 16.0427807487 | 0.000 % | `stable` |
| `CardiacOutput_L_min` | 6.1423258649 | 6.1255737711 | −0.273 % | `stable` |
| `BloodVolume_mL` | 5488.4311032949 | 5490.7753221464 | +0.043 % | `stable` |

---

## P1 – jednoduchý prompt

### Porovnanie trendov

| Parameter | Očakávaný trend | LLM | Výsledok |
|---|---|---|---|
| `HeartRate_bpm` | `increase` | `decrease` | ❌ |
| `ArterialPressure_mmHg` | `increase` | `increase` | ✅ |
| `MeanArterialPressure_mmHg` | `increase` | `increase` | ✅ |
| `SystolicPressure_mmHg` | `increase` | `increase` | ✅ |
| `DiastolicPressure_mmHg` | `decrease` | `decrease` | ✅ |
| `OxygenSaturation` | `stable` | `stable` | ✅ |
| `RespirationRate_bpm` | `stable` | `stable` | ✅ |
| `CardiacOutput_L_min` | `stable` | `decrease` | ❌ |
| `BloodVolume_mL` | `stable` | `decrease` | ❌ |

**Trend accuracy:** **66,7 %**  
**Response time:** **16,13 s**

### Summary

> The physiological data shows a general increase in blood pressure and cardiac output, but with some fluctuations.

### Interpretation

> The increases in arterial pressure, mean arterial pressure, systolic pressure, and cardiac output suggest an increase in cardiovascular activity. However, the decreases in diastolic pressure and blood volume indicate a potential decrease in overall circulation. The stable values for oxygen saturation and respiration rate suggest that these parameters are within normal limits.

### Limitations

> This analysis is based on a limited dataset and may not be representative of the entire population or situation.

---

## P2 – štruktúrovaný prompt

### Porovnanie trendov

| Parameter | Očakávaný trend | LLM | Výsledok |
|---|---|---|---|
| `HeartRate_bpm` | `increase` | `increase` | ✅ |
| `ArterialPressure_mmHg` | `increase` | `increase` | ✅ |
| `MeanArterialPressure_mmHg` | `increase` | `increase` | ✅ |
| `SystolicPressure_mmHg` | `increase` | `increase` | ✅ |
| `DiastolicPressure_mmHg` | `decrease` | `decrease` | ✅ |
| `OxygenSaturation` | `stable` | `stable` | ✅ |
| `RespirationRate_bpm` | `stable` | `stable` | ✅ |
| `CardiacOutput_L_min` | `stable` | `increase` | ❌ |
| `BloodVolume_mL` | `stable` | `increase` | ❌ |

**Trend accuracy:** **77,8 %**  
**Response time:** **12,70 s**

### Summary

> The physiological data shows an overall increase in heart rate, arterial pressure, mean arterial pressure, systolic pressure, and cardiac output. However, diastolic pressure decreases slightly. Oxygen saturation remains stable, while respiration rate and blood volume remain relatively stable.

### Interpretation

> These changes may indicate a response to physical activity or stress. Further analysis is needed to determine the underlying cause of these changes.

### Limitations

> The data only spans two time points (0s and 60s), which may not be sufficient to capture long-term trends or fluctuations.

---

## P3 – štruktúrovaný prompt + explicitný zákaz halucinácií

### Porovnanie trendov

| Parameter | Očakávaný trend | LLM | Výsledok |
|---|---|---|---|
| `HeartRate_bpm` | `increase` | `increase` | ✅ |
| `ArterialPressure_mmHg` | `increase` | `increase` | ✅ |
| `MeanArterialPressure_mmHg` | `increase` | `increase` | ✅ |
| `SystolicPressure_mmHg` | `increase` | `increase` | ✅ |
| `DiastolicPressure_mmHg` | `decrease` | `decrease` | ✅ |
| `OxygenSaturation` | `stable` | `stable` | ✅ |
| `RespirationRate_bpm` | `stable` | `stable` | ✅ |
| `CardiacOutput_L_min` | `stable` | `increase` | ❌ |
| `BloodVolume_mL` | `stable` | `increase` | ❌ |

**Trend accuracy:** **77,8 %**  
**Response time:** **12,60 s**

### Summary

> The physiological data shows an overall increase in heart rate, arterial pressure, mean arterial pressure, systolic pressure, and cardiac output. However, diastolic pressure decreases slightly. Oxygen saturation remains stable, while respiration rate and blood volume remain relatively stable.

### Interpretation

> These changes may indicate a stress response or increased physical activity, but further analysis is needed to determine the underlying cause.

### Limitations

> The data only provides two measurements, which may not be representative of the entire physiological process. Additionally, there is no information on potential confounding variables or individual patient characteristics.

---

## Finálne porovnanie promptovacích stratégií

| Prompt | Trend accuracy | Response time |
|---|---:|---:|
| **P1** | 66,7 % | 16,13 s |
| **P2** | 77,8 % | 12,70 s |
| **P3** | 77,8 % | 12,60 s |

Výsledný súhrn bol uložený do súboru:

`prompt_comparison_acute_stress_llama3.2.json`

### Predbežné pozorovanie

Štruktúrované prompty **P2 a P3** dosiahli v tomto pilotnom experimente vyššiu presnosť identifikácie trendov než jednoduchý prompt **P1**.

Rozdiel medzi P2 a P3 sa však nedá hodnotiť iba pomocou `trend accuracy`. Hlavným cieľom stratégie P3 je obmedziť nepodložené tvrdenia a halucinácie, preto je potrebné túto vlastnosť vyhodnocovať samostatne z textových odpovedí modelu.

Výsledky jedného scenára zatiaľ nemožno považovať za všeobecný záver o kvalite jednotlivých promptovacích stratégií.

[prompt_comparison_acute_stress_llama3.2.json
](llm/prompt_comparison_acute_stress_llama3.2.json
)

## Pilotné porovnanie promptovacích stratégií – Llama 3.2 / `acute_stress.json`

Na scenári `acute_stress.json` boli porovnané tri promptovacie stratégie pri rovnakom modeli **Llama 3.2**.

| Stratégia | Popis | Presnosť trendov | Čas odpovede |
|---|---|---:|---:|
| **P1** | jednoduchý prompt | 66,7 % | 16,13 s |
| **P2** | štruktúrovaný prompt | 77,8 % | 12,70 s |
| **P3** | štruktúrovaný prompt + explicitný zákaz halucinácií | 77,8 % | 12,60 s |

### Predbežný záver

Štruktúrovanie promptu zlepšilo presnosť identifikácie trendov približne o **11 percentuálnych bodov** oproti jednoduchému promptu.

Stratégie **P2** a **P3** dosiahli rovnakú presnosť identifikácie trendov. Explicitný zákaz halucinácií teda v tomto konkrétnom teste nepriniesol ďalšie zlepšenie numerickej klasifikácie trendov.

P3 však nemožno hodnotiť iba podľa metriky `trend_accuracy`. Jeho hlavný prínos sa má prejaviť najmä v znížení nepodložených tvrdení a halucinácií, čo je potrebné posudzovať samostatne na základe textových odpovedí modelu.

Zaujímavé je aj to, že P2 a P3 boli v tomto teste rýchlejšie než P1. Z výsledku jedného scenára však nemožno vyvodiť všeobecný záver o rýchlosti jednotlivých promptovacích stratégií.

> Výsledok zatiaľ naznačuje, že **štruktúrovaný prompt môže viesť k spoľahlivejšiemu spracovaniu fyziologických dát než jednoduché zadanie**, tento záver je však potrebné overiť na väčšom počte scenárov.