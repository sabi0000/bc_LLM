# Príprava a spracovanie dát
| JSON/test case | Pulse scenár | Prečo ho chceme |
|---|---|---|
| `normal.json` | `HowTo_EngineUse.py` alebo stav pacienta pred zásahom | zdravý baseline |
| `acute_stress.json` | `HowTo_AcuteStress.py` | zvýšenie HR, prípadne tlaku |
| `hemorrhage.json` | `HowTo_Hemorrhage.py` | HR ↑, MAP/BP ↓, cardiac output ↓, blood volume ↓ |
| `heart_failure.json` | `HowTo_ChronicVentricularSystolicDysfunction.py` | stroke volume ↓, cardiac output ↓, tlak ↓ |
| `pericardial_effusion.json` | `HowTo_PericardialEffusion.py` | CO/SV/tlak ↓ + kompenzačné zvýšenie HR |
| `low_oxygen.json` | `HowTo_ImpairedAlveolarExchange.py` | narušená výmena plynov, vhodné na prípad s nízkou oxygenáciou |

Konverzia na json:
[CSV_TO_JSON](llm/ccsv_to_json.py)
