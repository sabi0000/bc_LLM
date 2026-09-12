Tento repozitár slúži ako pracovný priestor k vedeniu bakalárskej práce zameranej na využitie lokálnych veľkých jazykových modelov (LLM) pri analýze a interpretácii fyziologických simulačných dát.

Repozitár obsahuje moje priebežné technické overovanie realizovateľnosti témy, prototypy, testovacie dáta, výsledky experimentov a poznámky k ďalšiemu smerovaniu bakalárskej práce.

# Zadanie práce
S rozvojom konceptu ľudských digitálnych dvojčiat (Human-Digital Twin) v doméne moderného zdravotníctva a biomechatroniky vzniká potreba intuitívnejšej interakcie medzi lekárom a komplexnými systémami. Tradičné výstupy zo simulácií biosignálov sú často náročné na rýchlu klinickú interpretáciu, čo táto práca rieši návrhom inovatívneho komunikačného rozhrania na báze lokálnych veľkých jazykových modelov (LLM). Hlavným cieľom je vytvoriť bezpečný, plne offline fungujúci systém, ktorý dokáže autonómne transformovať simulované dáta kardiovaskulárneho systému do zrozumiteľnej prirodzenej reči a asistovať pri identifikácii anomálií.
 
Úlohy:
1. Vytvorte rozbor súčasného stavu využitia veľkých jazykových modelov a umelej inteligencie v oblasti  digitálnej diagnostiky a konceptu ľudských digitálnych dvojčiat (Human-Digital Twin).
 
2. Navrhnite a realizujte lokálne nasadenie (on-premise) vybraného open-source jazykového modelu s dôrazom na absenciu cloudového pripojenia a prísnu ochranu citlivých dát.
 
3. Implementujte softvérové komunikačné rozhranie, ktoré bude s využitím techník pokročilého prompt inžinierstva dynamicky transformovať štruktúrované výstupy do kontextového vstupu pre LLM.
 
4. Navrhnite metodiku testovania a vykonajte experimentálne vyhodnotenie vyvinutého rozhrania. Analyzujte presnosť a relevanciu generovaných reportov pri simulovanej interakcii s používateľom a kvantifikujte mieru výskytu sémantických odchýlok (halucinácií LLM).

# Základná navrhovaná pipeline:

Pulse Physiology Engine

↓

fyziologické dáta

↓

Python preprocessing

↓

JSON / štruktúrované charakteristiky

↓

lokálny LLM

↓

textová interpretácia / report


LLM má pracovať iba s poskytnutými dátami a nemala by dopĺňať chýbajúce hodnoty, symptómy, diagnózy ani iné informácie, ktoré zo vstupných dát nemožno odvodiť.

# Použité technológie
- Pulse Physiology Engine
- Docker
- Python
- Ollama
- Llama 3.2
- JSON / CSV

# Jednotlivé body
1. PULSE  `1_pulse.md`
2. OLLAMA `2_ollama.md` 
3. PRÍPRAVA A SPRACOVANIE DÁT `3_preprocessing.md`
4. PRIDANIE DAT DO LLM `4_data_add.md`
5. VYHODNOCOVACIE SCENÁRE `5_vyhodnotenie.md`

# Plán práce
- Týždne 1–2:  
Ollama + prvý LLM prototyp + syntetické JSON dáta.

- Týždne 3–4: 
Pulse Physiology Engine. Rozbehať jeden normálny scenár a dostať z neho CSV s HR, BP, MAP, SpO₂, cardiac output atď.

- Týždne 5–6: napojiť:
Pulse → parser → JSON → prompt → LLM
A spraviť jednoduché používateľské rozhranie. Nemusí byť nádherné; pokojne Streamlit/Gradio alebo jednoduchá desktop/web app.

- Týždne 7–8: prompt engineering. 
Napríklad porovnať:
    - jednoduchý prompt, 
    - štruktúrovaný prompt, 
	- prompt s explicitným zákazom domýšľania informácií. 


- Týždne 9–10: 
vytvoriť testovací dataset/scenáre. Napríklad 30–50 simulácií:
normal / tachycardia / hypotension / hemorrhage / kombinované stavy / chýbajúce údaje
Pulse vie simulovať aj rôzne fyziologické stavy, akcie, zranenia a intervencie, takže sa to dá neskôr pekne rozšíriť. 

- Týždne 11–12: vyhodnotenie:
	-  správnosť, 
	-  relevancia, 
	-  halucinácie, 
	-  odpoveď na otázky, 
	- porovnanie promptov, 
	- prípadne porovnanie dvoch LLM. 





# Aktuálny stav

- [x] Spustenie Pulse Physiology Engine v Dockeri
- [x] Spustenie lokálneho LLM pomocou Ollama
- [x] Základný test modelu Llama 3.2
- [x] Získanie fyziologických dát zo simulácií
- [x] Konverzia výstupov do CSV a JSON
- [x] Vytvorenie prototypu JSON → prompt → LLM
- [x] Jednoduchý chat nad fyziologickými dátami
- [x] Vytvorenie základného evaluačného skriptu
- [x] Automatický výpočet ground truth trendov v Pythone
- [x] Pilotné porovnanie promptovacích stratégií
- [ ] Rozšírenie počtu testovacích scenárov
- [ ] Porovnanie viacerých lokálnych LLM
- [ ] Podrobnejšie vyhodnotenie halucinácií
- [ ] Finalizácia experimentálnej metodiky bakalárskej práce

