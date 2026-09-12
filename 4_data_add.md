# PRIDANIE DAT DO LLM
Workflow
```
Vyber simuláciu:

1 - acute_stress.json
2 - hemorrhage.json
3 - normall.json
4 - pericardial.json
5 - ventriculal.json

Vyber: 2

Dáta načítané.

Ty: What happened to blood volume?

LLM: Blood volume decreased from...

Ty: What happened to cardiac output?

LLM: Cardiac output slightly decreased...

Ty: Is there enough evidence to determine the cause?

LLM: No. The provided measurements show...
``` 

[SCRIPT](llm/chat_with_data.py)

Test scenár:
``` 
	Dostupne simulacie:
	
	1. acute_stress.json
	2. hemorrhage.json
	3. normall.json
	4. pericardial.json
	5. simulation_summary.json
	6. ventriculal.json
	
	Vyber cislo simulacie: 
	>>> 2
	Nacitane data zo suboru: hemorrhage.json
	Pocet zaznamov: 2
	
	LLM:
	I'm ready to analyze the physiological simulation data with you. What's the first question or topic you'd like to discuss based on this data?
	
	Mozes sa pytat na data.
	Pre ukoncenie napis: exit
	Ty: What are the most significant changes in the data?
	LLM:
	From the provided data, I notice two significant changes:
	
	1. A decrease in CardiacOutput_L_min from 6.14 L/min at Time_s = 0 to 6.02 L/min at Time_s = 30.
	2. An increase in HeartRate_bpm from 84 bpm at Time_s = 0 to 84.98 bpm at Time_s = 30.
	
	These changes occurred over a time period of 30 seconds, suggesting that the cardiac output and heart rate changed within this short timeframe.
	Ty: Which cardiovascular parameter changed the most?
	LLM:
	To determine which parameter changed the most, I'll compare the absolute differences between the corresponding values before and after Time_s = 0.
	
	HeartRate_bpm:
	Old value: 84 bpm
	New value: 84.98 bpm
	Difference: 0.98 bpm
	
	CardiacOutput_L_min:
	Old value: 6.14 L/min
	New value: 6.02 L/min
	Difference: 0.12 L/min
	
	MeanArterialPressure_mmHg and BloodVolume_mL remained relatively stable.
	
	The HeartRate_bpm changed the most, with an increase of approximately 1.18% (from 84 to 84.98).
	Ty: Is oxygen saturation stable?
	LLM:
	I don't have information on oxygen saturation in the provided data. Oxygen saturation is not included in the measurements you shared.
	Ty: Summarize the simulation in three sentences.
	LLM:
	The cardiovascular parameters heart rate and cardiac output showed a slight increase within a 30-second time period, with heart rate increasing from 84 to 84.98 beats per minute. Meanwhile, blood volume decreased slightly, dropping from approximately 5488.43 mL at Time_s = 0 to around 5378.13 mL at Time_s = 30. The mean arterial pressure remained relatively stable throughout the observed time period.

``` 

