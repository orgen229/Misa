# POIT IoT webová aplikácia na monitorovanie teploty a vlhkosti a riadenie ventilátora

## 1. Popis projektu

Tento projekt bol vytvorený ako záverečné zadanie z predmetu **POIT**. Cieľom projektu je monitorovať a riadiť signály získané z reálneho hardvéru prostredníctvom webovej aplikácie v súlade s koncepciou IoT.

Systém meria **teplotu** a **relatívnu vlhkosť vzduchu** pomocou snímača **DHT11**, ktorý je pripojený k mikrokontroléru **ESP32**. ESP32 odosiela namerané údaje cez Wi-Fi sieť na serverovú aplikáciu vytvorenú v jazyku Python pomocou frameworku **Flask**.

Okrem monitorovania je v projekte realizované aj jednoduché riadenie akčného člena. Ak nameraná teplota prekročí nastavenú hranicu, pomocou relé modulu sa zapne 5V ventilátor. Pri poklese teploty pod dolnú hranicu sa ventilátor vypne. Ide o dvojpolohovú reguláciu s hysteréziou.

Projekt realizuje celý reťazec:

```text
DHT11 → ESP32 → Wi-Fi / HTTP JSON → Flask server → SQLite + CSV → Web dashboard
```

## 2. Hlavné funkcie aplikácie

Webová aplikácia realizuje požadované funkcie zadania:

| Bod zadania | Funkcia | Realizácia v projekte |
|---|---|---|
| 1 | Open | Inicializácia systému tlačidlom `Open` |
| 2 | Nastavenie parametrov | Nastavenie prahov ventilátora a intervalu merania |
| 3 | Start | Spustenie monitorovania tlačidlom `Start` |
| 4 | Zoznam údajov | Tabuľka posledných meraní |
| 5 | Grafy | Graf teploty a graf vlhkosti pomocou Chart.js |
| 6 | Ručičkové ukazovatele | Gauge ukazovatele pre teplotu a vlhkosť |
| 7 | Archivácia do databázy | Ukladanie meraní do SQLite databázy |
| 8 | Archivácia do súboru | Ukladanie meraní do CSV súboru |
| 9 | Stop | Zastavenie monitorovania tlačidlom `Stop` |
| 10 | Close | Deaktivácia systému tlačidlom `Close` |

## 3. Použitý hardvér

| Komponent | Účel |
|---|---|
| ESP32 NodeMCU 38-pin s CP2102 | Mikrokontrolér s Wi-Fi pripojením |
| DHT11 | Snímač teploty a vlhkosti |
| Relé modul 5V | Spínanie ventilátora |
| Ventilátor 5V | Akčný člen pre jednoduché chladenie |
| Nepájivé pole | Zapojenie komponentov bez spájkovania |
| Dupont vodiče | Prepojenie komponentov |
| USB-C kábel | Napájanie a nahratie firmvéru |

## 4. Použitý softvér

| Technológia | Účel |
|---|---|
| Arduino IDE | Vývoj a nahratie firmvéru do ESP32 |
| Python | Serverová časť |
| Flask | Webový server a REST API |
| SQLite | Databázová archivácia meraní |
| CSV | Súborová archivácia meraní |
| HTML / CSS / JavaScript | Klientska časť |
| Chart.js | Vykreslenie grafov |
| GitHub | Verzionovanie projektu |

## 5. Architektúra systému

Architektúra pozostáva z troch hlavných vrstiev:

1. **Hardvérová vrstva**
   - DHT11 snímač
   - ESP32
   - relé modul
   - ventilátor

2. **Serverová vrstva**
   - Flask server
   - REST API
   - SQLite databáza
   - CSV súbor

3. **Klientska vrstva**
   - webový dashboard
   - grafy
   - tabuľka údajov
   - ručičkové ukazovatele
   - ovládacie tlačidlá

Diagram architektúry je uložený v priečinku:

```text
docs/architecture.png
```

## 6. UML diagramy

Projekt obsahuje UML diagramy potrebné pre technickú dokumentáciu:

```text
docs/uml_use_case_diagram.png
docs/uml_component_diagram.png
docs/uml_sequence_diagram.png
```

### UML diagram prípadov použitia

Zobrazuje hlavné funkcie systému z pohľadu používateľa:

- Open system
- Nastaviť parametre
- Start monitorovania
- Zobraziť zoznam meraní
- Zobraziť grafy
- Zobraziť ručičkové ukazovatele
- Stiahnuť CSV
- Stop monitorovania
- Close system

### UML komponentový diagram

Zobrazuje hlavné komponenty systému:

- DHT11 snímač
- ESP32 firmvér
- Relé modul
- Ventilátor
- Flask server
- SQLite databáza
- CSV súbor
- Web dashboard

### UML sekvenčný diagram

Zobrazuje komunikáciu medzi používateľom, webovým dashboardom, serverom, ESP32, snímačom a archivačnými časťami systému.

## 7. Zapojenie hardvéru

Schéma zapojenia je uložená v súbore:

```text
docs/schema.png
```

### DHT11 → ESP32

| DHT11 | ESP32 |
|---|---|
| VCC | 3V3 |
| GND | GND |
| DATA | GPIO22 |

### Relé modul → ESP32

| Relé modul | ESP32 |
|---|---|
| VCC | VIN 5V |
| GND | GND |
| IN | GPIO23 |

### Ventilátor cez relé

| Prvok | Zapojenie |
|---|---|
| COM relé | 5V |
| NO relé | kladný vodič ventilátora |
| záporný vodič ventilátora | GND |
| NC relé | nepoužíva sa |

Relé je použité ako spínač napájania ventilátora. Ventilátor je pripojený na kontakty **COM** a **NO**, aby bol v pokojovom stave vypnutý.

## 8. Firmvér ESP32

Firmvér sa nachádza v priečinku:

```text
firmware/esp32_dht11_http/esp32_dht11_http.ino
```

Firmvér zabezpečuje:

- pripojenie ESP32 k Wi-Fi sieti,
- čítanie údajov zo snímača DHT11,
- získavanie konfiguračných parametrov zo servera,
- riadenie ventilátora pomocou relé,
- vytváranie JSON správy,
- odosielanie údajov na Flask server pomocou HTTP POST.

Pred nahratím firmvéru je potrebné nastaviť Wi-Fi údaje a adresu servera:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_BASE_URL = "http://YOUR_SERVER_IP:5000";
```

Reálne heslá a lokálne IP adresy nemajú byť uložené vo verejnom repozitári.

## 9. Regulácia ventilátora

Ventilátor je riadený pomocou dvojpolohovej regulácie s hysteréziou.

Predvolené hodnoty:

```text
Fan ON threshold  = 33 °C
Fan OFF threshold = 32 °C
```

Logika:

```text
teplota >= 33 °C → ventilátor ON
teplota <= 32 °C → ventilátor OFF
```

Hysterézia zabraňuje častému prepínaniu relé v prípade, že sa teplota pohybuje okolo jednej hranice.

Parametre je možné upraviť priamo vo webovej aplikácii.

## 10. Komunikačný protokol

ESP32 komunikuje so serverom pomocou protokolu HTTP.

Použité endpointy:

| Endpoint | Metóda | Popis |
|---|---|---|
| `/api/data` | POST | Príjem údajov z ESP32 |
| `/api/config` | GET | Získanie nastavení pre ESP32 |
| `/api/config` | POST | Zmena nastavení z webového rozhrania |
| `/api/open` | POST | Inicializácia systému |
| `/api/start` | POST | Spustenie monitorovania |
| `/api/stop` | POST | Zastavenie monitorovania |
| `/api/close` | POST | Ukončenie systému |
| `/api/latest` | GET | Posledné meranie |
| `/api/history` | GET | Historické merania |
| `/api/file-history` | GET | Údaje uložené v CSV |
| `/api/download-csv` | GET | Stiahnutie CSV súboru |

Príklad JSON správy z ESP32:

```json
{
  "temperature": 30.20,
  "humidity": 44.00,
  "unit_temperature": "C",
  "unit_humidity": "%",
  "sensor": "DHT11",
  "fan_state": "OFF"
}
```

## 11. Serverová časť

Serverová časť sa nachádza v priečinku:

```text
server/
```

Hlavný súbor:

```text
server/app.py
```

Server zabezpečuje:

- zobrazenie webového dashboardu,
- spracovanie tlačidiel Open / Start / Stop / Close,
- spracovanie nastavenia parametrov,
- príjem údajov z ESP32,
- uloženie údajov do SQLite databázy,
- zápis údajov do CSV súboru,
- poskytovanie aktuálnych a historických údajov klientovi.

## 12. Databáza SQLite

Databázový súbor:

```text
measurements.db
```

Databáza sa vytvorí automaticky pri spustení servera.

Tabuľka `measurements` obsahuje:

| Stĺpec | Popis |
|---|---|
| id | Primárny kľúč |
| temperature | Nameraná teplota |
| humidity | Nameraná vlhkosť |
| sensor | Názov snímača |
| unit_temperature | Jednotka teploty |
| unit_humidity | Jednotka vlhkosti |
| fan_state | Stav ventilátora |
| fan_on_threshold | Prah zapnutia ventilátora |
| fan_off_threshold | Prah vypnutia ventilátora |
| timestamp | Čas prijatia merania |

## 13. CSV archivácia

Okrem databázy sa merania ukladajú aj do súboru:

```text
measurements.csv
```

CSV súbor je možné:

- zobraziť vo webovej aplikácii,
- stiahnuť pomocou tlačidla `Stiahnuť CSV`.

## 14. Klientska časť

Klientska časť sa nachádza v súbore:

```text
server/templates/index.html
```

Dashboard obsahuje:

- tlačidlá Open / Start / Stop / Close,
- formulár na nastavenie parametrov,
- aktuálnu teplotu,
- aktuálnu vlhkosť,
- stav ventilátora,
- čas posledného merania,
- graf teploty,
- graf vlhkosti,
- ručičkové ukazovatele,
- tabuľku meraní,
- prepínanie režimu histórie,
- zobrazenie údajov z CSV,
- stiahnutie CSV súboru.

## 15. Historické údaje

Dashboard podporuje dva režimy zobrazenia histórie:

```text
Posledných 20 meraní
Posledných 24 hodín
```

Tým je splnená požiadavka na zobrazenie historických údajov za zvolené časové obdobie.

## 16. Inštalácia serverovej časti

Prejdite do priečinka servera:

```bash
cd server
```

Vytvorte virtuálne prostredie:

```bash
python3 -m venv venv
```

Aktivujte virtuálne prostredie:

Linux / Raspberry Pi:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Nainštalujte závislosti:

```bash
pip install -r requirements.txt
```

Spustite server:

```bash
python3 app.py
```

Server bude dostupný na adrese:

```text
http://127.0.0.1:5000/
```

## 17. Nahratie firmvéru do ESP32

1. Otvoriť Arduino IDE.
2. Nainštalovať podporu pre ESP32 dosky.
3. Vybrať dosku `ESP32 Dev Module`.
4. Vybrať správny COM port.
5. Nainštalovať knižnice:
   - `DHT sensor library`
   - `Adafruit Unified Sensor`
6. Upraviť Wi-Fi údaje a IP adresu servera.
7. Nahrať firmvér do ESP32.

Ak sa nahrávanie zasekne na `Connecting...`, je možné podržať tlačidlo `BOOT` na ESP32.

## 18. Spustenie celého systému

Odporúčaný postup:

1. Spustiť Flask server:

```bash
cd server
python3 app.py
```

2. Otvoriť dashboard:

```text
http://127.0.0.1:5000/
```

3. Pripojiť ESP32 k napájaniu.
4. Na dashboarde stlačiť tlačidlo `Open`.
5. Nastaviť parametre regulácie.
6. Stlačiť tlačidlo `Start`.
7. Sledovať tabuľku, grafy a ručičkové ukazovatele.
8. Podľa potreby stiahnuť CSV súbor.
9. Tlačidlom `Stop` zastaviť monitorovanie.
10. Tlačidlom `Close` deaktivovať systém.

## 19. Štruktúra repozitára

Odporúčaná štruktúra:

```text
/
├── firmware/
│   └── esp32_dht11_http/
│       └── esp32_dht11_http.ino
├── server/
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       └── index.html
├── docs/
│   ├── architecture.png
│   ├── schema.png
│   ├── uml_use_case_diagram.png
│   ├── uml_component_diagram.png
│   ├── uml_sequence_diagram.png
│   └── dashboard_screenshot.png
├── sketch_apr29a/
├── README.md
├── Technicka_dokumentacia_POIT.tex
└── .gitignore
```

## 20. Technická dokumentácia

Technická dokumentácia pre POIT je pripravená vo formáte LaTeX:

```text
Technicka_dokumentacia_POIT.tex
```

Dokumentácia obsahuje:

- úvod,
- cieľ zadania,
- použitý hardvér a softvér,
- architektúru systému,
- UML diagramy,
- hardvérové zapojenie,
- serverovú časť,
- klientskú časť,
- databázu a CSV archiváciu,
- používateľskú príručku,
- vývojársku príručku,
- testovanie,
- záver.

## 21. Testovanie

Systém bol testovaný postupne:

1. Čítanie údajov zo snímača DHT11.
2. Testovanie relé pomocou samostatného sketchu.
3. Pripojenie ESP32 k Wi-Fi sieti.
4. Odosielanie JSON dát na Flask server.
5. Ukladanie údajov do SQLite databázy.
6. Zápis údajov do CSV súboru.
7. Zobrazenie údajov v tabuľke.
8. Zobrazenie grafov.
9. Zobrazenie ručičkových ukazovateľov.
10. Ovládanie systému tlačidlami Open / Start / Stop / Close.

## 22. Testovací sketch relé

Priečinok:

```text
sketch_apr29a/
```

obsahuje testovací sketch, ktorý bol použitý na overenie funkčnosti relé modulu a ventilátora. Slúži iba ako pomocný vývojový súbor a nie je hlavnou časťou finálneho systému.

## 23. GitHub a verzionovanie

Pri vývoji bol použitý GitHub. Jednotlivé zmeny sú ukladané ako commity s popisom vykonanej práce.

Repozitár:

```text
https://github.com/orgen229/Misa
```

Pred odovzdaním treba skontrolovať, že repozitár neobsahuje:

- reálne Wi-Fi heslá,
- súbor `measurements.db`,
- súbor `measurements.csv`,
- virtuálne prostredie Python,
- dočasné súbory.

## 24. .gitignore

Odporúčaný obsah `.gitignore`:

```gitignore
__pycache__/
*.pyc
*.pyo
*.pyd

measurements.db
measurements.csv
*.db

.env
venv/
.venv/

.DS_Store
Thumbs.db
```

## 25. Možné rozšírenia

Možné rozšírenia projektu:

- použitie presnejšieho snímača DHT22 alebo BME280,
- použitie MQTT protokolu,
- autentifikácia používateľa,
- HTTPS komunikácia,
- nasadenie servera na cloud,
- export údajov do ďalších formátov,
- samostatná mobilná verzia dashboardu,
- podrobnejšie logovanie chýb.

## 26. Autor

```text
Ablazov Yehor
```

Predmet:

```text
POIT
```
