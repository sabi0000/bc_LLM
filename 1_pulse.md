# Pulse Physiology Engine
Pulse Physiology Engine je open-source nástroj určený na simuláciu ľudskej fyziológie. Umožňuje dynamicky modelovať správanie viacerých vzájomne prepojených fyziologických systémov, napríklad kardiovaskulárneho, respiračného, renálneho či endokrinného systému.

V rámci tejto práce sa Pulse používa ako zdroj syntetických fyziologických dát. Pomocou pripravených simulačných scenárov je možné sledovať vývoj vybraných parametrov, napríklad:

- srdcovej frekvencie,
- arteriálneho tlaku,
- stredného arteriálneho tlaku,
- saturácie kyslíkom,
- respiračnej frekvencie,
- srdcového výdaja,
- objemu krvi.

https://pulse.kitware.com/
https://hub.docker.com/r/kitware/pulse

Stiahnitie:
`docker pull kitware/pulse:4.3.1`

Rozbeh:
`docker run --rm -it kitware/pulse:4.3.1`

Zobrazenie kontajnerov:
`docker ps -a`

Nastartovanie kontajnera:
`docker start pulse-dev`

Vojdem do kontajnera:
`docker exec -it pulse-dev bash`
Zobrazí sa:
`root@3126a22db11e:/#`

Cd do prikladov:
`cd /pulse/python/pulse/howto`

Výpis scenárov: `ls`
### Dostupné Pulse `HowTo` scenáre

```text
HowTo_ARDS.py                                  HowTo_EngineUse.py                 HowTo_RespiratoryFatigue.py
HowTo_AcuteStress.py                           HowTo_EnvironmentalConditions.py   HowTo_RespiratoryMechanics.py
HowTo_AirwayObstruction.py                     HowTo_Exercise.py                  HowTo_RespiratoryModification.py
HowTo_Anemia.py                                HowTo_Hemorrhage.py                
HowTo_Sepsis.py
HowTo_Arrhythmia_CPR.py                        HowTo_Hemothorax.py                HowTo_SubstanceBolus.py
HowTo_AsthmaAttack.py                          HowTo_ImpairedAlveolarExchange.py  HowTo_SubstanceCompoundInfusion.py
HowTo_BagValveMask.py                          HowTo_Intubation.py                HowTo_SubstanceInfusion.py
HowTo_BrainInjury.py                           HowTo_MechanicalVentilation.py     HowTo_SupplementalOxygen.py
HowTo_Bronchoconstriction.py                   HowTo_MechanicalVentilator.py      HowTo_SystemModifiers.py
HowTo_COPD.py                                  HowTo_MultiplexVentilation.py      HowTo_TensionPneumothroax.py
HowTo_CardiovascularModification.py            HowTo_PatientPool.py               HowTo_ThermalApplication.py
HowTo_ChronicVentricularSystolicDysfunction.py HowTo_PericardialEffusion.py       
HowTo_Urinate.py
HowTo_ConsciousRespiration.py                  HowTo_Pneumonia.py                 HowTo_UseThreadPools.py
HowTo_ConsumeNutrients.py                      HowTo_ProcessResults.py            HowTo_VentilationMechanics.py
HowTo_Dehydration.py                           HowTo_PulmonaryFibrosis.py          
HowTo_Dyspnea.py                               HowTo_PulmonaryShunt.py            
HowTo_ECMO.py                                  HowTo_RenalStenosis.py
```

Prepneme sa do priecinka:
`cd /pulse/bin`

Pustime simulaciu: 
`python3 /pulse/python/pulse/howto/HowTo_AcuteStress.py > acute_stress.txt 2>&1
`

Vytvorime konvertovaci subor:
 ```
 cat > pulse_log_to_csv.py <<'PY'
import re
import csv
import sys

if len(sys.argv) != 3:
    print("Pouzitie: python3 pulse_log_to_csv.py input.txt output.csv")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

fields = {
    "HeartRate": "HeartRate_bpm",
    "ArterialPressure": "ArterialPressure_mmHg",
    "MeanArterialPressure": "MeanArterialPressure_mmHg",
    "SystolicArterialPressure": "SystolicPressure_mmHg",
    "DiastolicArterialPressure": "DiastolicPressure_mmHg",
    "OxygenSaturation": "OxygenSaturation",
    "RespirationRate": "RespirationRate_bpm",
    "CardiacOutput": "CardiacOutput_L_min",
    "BloodVolume": "BloodVolume_mL"
}

rows = []
current = None

with open(input_file, "r", errors="ignore") as f:
    for line in f:

        m = re.match(r"SimulationTime\(s\)=([0-9eE+.\-]+)", line.strip())
        if m:
            if current is not None:
                rows.append(current)

            current = {
                "Time_s": float(m.group(1))
            }
            continue

        if current is None:
            continue

        for pulse_name, csv_name in fields.items():

            # hodnoty s jednotkou, napr.
            # HeartRate(1/min)=84.0
            pattern_unit = rf"^{re.escape(pulse_name)}\([^)]*\)=([0-9eE+.\-]+)"

            # hodnoty bez jednotky, napr.
            # OxygenSaturation=0.97
            pattern_plain = rf"^{re.escape(pulse_name)}=([0-9eE+.\-]+)"

            m = re.match(pattern_unit, line.strip())

            if not m:
                m = re.match(pattern_plain, line.strip())

            if m:
                current[csv_name] = float(m.group(1))

if current is not None:
    rows.append(current)

headers = [
    "Time_s",
    "HeartRate_bpm",
    "ArterialPressure_mmHg",
    "MeanArterialPressure_mmHg",
    "SystolicPressure_mmHg",
    "DiastolicPressure_mmHg",
    "OxygenSaturation",
    "RespirationRate_bpm",
    "CardiacOutput_L_min",
    "BloodVolume_mL"
]

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

    for row in rows:
        writer.writerow(row)

print(f"Hotovo: {output_file}")
print(f"Pocet casovych bodov: {len(rows)}")
PY
 ```

 Prekonverujeme txt do csv:

`python3 pulse_log_to_csv.py acute_stress.txt acute_stress.csv`


Skontrolujeme vypis:

`cat acute_stress.csv`


Skopirovanie na plochu:

Vyjdeme z dockera
`exit`

`docker cp pulse-dev:/pulse/bin/hemorrhage.csv "C:\Users\sabin\OneDrive\Počítač\hemorrhage.csv"`



