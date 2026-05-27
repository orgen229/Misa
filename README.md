# IoT systém na meranie teploty a vlhkosti pomocou ESP32

## 1. Popis projektu

Tento projekt realizuje IoT systém na meranie fyzikálnych veličín pomocou reálneho hardvérového snímača. Systém meria teplotu a relatívnu vlhkosť vzduchu pomocou snímača DHT11, ktorý je pripojený k mikrokontroléru ESP32.

ESP32 sa pripája k Wi-Fi sieti a v pravidelnom intervale odosiela namerané hodnoty na serverovú aplikáciu vytvorenú v jazyku Python pomocou frameworku Flask. Dáta sú prenášané vo formáte JSON pomocou HTTP POST požiadavky.

Server prijaté merania ukladá do SQLite databázy spolu s časovou pečiatkou. Webové rozhranie zobrazuje aktuálne hodnoty, čas posledného merania, historické grafy a tabuľku posledných meraní.

Projekt pokrýva celý reťazec:

```text
fyzický snímač → ESP32 firmvér → Wi-Fi prenos → Flask server → SQLite databáza → webová vizualizácia
```

## 2. Merané veličiny

Systém meria tieto fyzikálne veličiny:

- teplota vzduchu v °C
- relatívna vlhkosť vzduchu v %

Použitý snímač DHT11 poskytuje digitálny výstup obsahujúci hodnotu teploty a vlhkosti.

## 3. Funkčné požiadavky

Projekt spĺňa nasledujúce požiadavky:

| Požiadavka | Splnenie v projekte |
|---|---|
| R1 — Meranie fyzikálnej veličiny | ESP32 meria teplotu a vlhkosť pomocou snímača DHT11 |
| R2 — Bezdrôtový prenos | Dáta sú prenášané cez Wi-Fi pomocou HTTP POST |
| R3 — Ukladanie dát | Dáta sú ukladané do SQLite databázy spolu s časovou pečiatkou |
| R4 — Webová vizualizácia | Webový dashboard zobrazuje aktuálne aj historické hodnoty |
| R5 — Dostupnosť | Dashboard môže byť sprístupnený pomocou ngrok tunela |

## 4. Použitý hardvér

| Komponent | Účel |
|---|---|
| ESP32 NodeMCU 38-pin s CP2102 | mikrokontrolérová platforma s Wi-Fi |
| DHT11 | snímač teploty a vlhkosti |
| Nepájivé pole | zapojenie bez spájkovania |
| Dupont vodiče | prepojenie komponentov |
| USB-C kábel | napájanie ESP32 a nahratie firmvéru |
| 5V relé modul | spínanie ventilátora |
| 5V ventilátor | akčný člen na jednoduché chladenie |
| LED dióda | voliteľná signalizácia stavu |

## 5. Odôvodnenie výberu hardvéru

### ESP32

ESP32 bol zvolený, pretože obsahuje integrované Wi-Fi rozhranie, dostatočný počet GPIO pinov a je vhodný pre IoT aplikácie. Umožňuje jednoduché pripojenie k bezdrôtovej sieti a odosielanie dát na server pomocou HTTP požiadaviek.

### DHT11

DHT11 bol zvolený z dôvodu jednoduchej dostupnosti, nízkej ceny a možnosti merať dve environmentálne veličiny jedným snímačom: teplotu a vlhkosť. Pre účely školského demonštračného IoT projektu je jeho presnosť postačujúca.

### Relé modul a ventilátor

Relé modul a 5V ventilátor sú použité ako jednoduchý akčný člen. Ventilátor sa zapne pri prekročení nastavenej teplotnej hranice a vypne sa po poklese teploty pod dolnú hranicu. Tým je demonštrované jednoduché riadenie podľa meranej veličiny.

## 6. Kategória snímača

Použitý snímač: **DHT11**

DHT11 je digitálny snímač teploty a vlhkosti. Komunikuje pomocou proprietárneho jednovodičového digitálneho protokolu. Výstup zo snímača je spracovaný priamo firmvérom ESP32 pomocou knižnice `DHT.h`.

Príklad získaných hodnôt:

```json
{
  "temperature": 30.2,
  "humidity": 44.0
}
```

## 7. Architektúra systému

Systém pozostáva z troch hlavných vrstiev:

1. **Snímacia vrstva**
   - ESP32
   - DHT11
   - relé modul
   - ventilátor

2. **Serverová vrstva**
   - Python Flask server
   - REST API
   - SQLite databáza

3. **Vizualizačná vrstva**
   - HTML webové rozhranie
   - JavaScript
   - Chart.js grafy

Diagram architektúry je uložený v súbore:

```text
docs/architecture.png
```

Zjednodušená architektúra:

```text
+---------+       +-------+       Wi-Fi / HTTP POST       +----------------+
| DHT11   | ----> | ESP32 | ----------------------------> | Flask server   |
+---------+       +-------+          JSON dáta            +----------------+
                                                               |
                                                               v
                                                        +---------------+
                                                        | SQLite DB     |
                                                        +---------------+
                                                               |
                                                               v
                                                        +---------------+
                                                        | Web dashboard |
                                                        +---------------+
```

## 8. Schéma zapojenia

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
| Relay COM | 5V |
| Relay NO | červený vodič ventilátora |
| čierny vodič ventilátora | GND |
| Relay NC | nepoužíva sa |

Relé je zapojené ako spínač napájania ventilátora. Používa sa kombinácia kontaktov COM a NO, aby bol ventilátor pri neaktívnom relé vypnutý.

## 9. Firmvér

Firmvér je programová časť nahraná priamo do mikrokontroléra ESP32.

V projekte firmvér zabezpečuje:

- inicializáciu snímača DHT11
- pripojenie ESP32 k Wi-Fi sieti
- pravidelné meranie teploty a vlhkosti
- vytvorenie JSON správy
- odosielanie dát na Flask server pomocou HTTP POST
- základné ošetrenie výpadku Wi-Fi pripojenia pomocou opätovného pripojenia
- riadenie ventilátora podľa nameranej teploty

Firmvér je vytvorený v prostredí **Arduino IDE**.

Umiestnenie hlavného firmvéru v repozitári:

```text
firmware/esp32_dht11_http/esp32_dht11_http.ino
```

## 10. Testovací sketch pre relé

V repozitári sa nachádza aj testovací sketch:

```text
sketch_apr29a/
```

Tento sketch slúžil na overenie funkčnosti relé modulu a ventilátora. Pomocou neho bolo možné samostatne otestovať, či relé reaguje na signál z ESP32 a či sa ventilátor správne zapína a vypína.

Tento súbor nie je hlavnou časťou finálneho systému, ale slúži ako pomocný testovací kód počas vývoja.

## 11. Perióda merania

Perióda merania bola nastavená na:

```text
5 sekúnd
```

Teplota a vlhkosť sa menia relatívne pomaly, preto nie je potrebné merať hodnoty v milisekundových intervaloch. Interval 5 sekúnd je vhodný pre demonštráciu počas obhajoby, pretože zmeny sú viditeľné dostatočne rýchlo a zároveň systém nevytvára zbytočne veľké množstvo dát.

## 12. Riadenie ventilátora

Ventilátor je riadený pomocou jednoduchej dvojpolohovej regulácie s hysteréziou.

Použitá logika:

```text
teplota >= 33 °C → ventilátor ON
teplota <= 32 °C → ventilátor OFF
```

Hysterézia zabraňuje tomu, aby sa relé a ventilátor príliš často zapínali a vypínali pri malej zmene teploty okolo jednej hranice.

Stav ventilátora je zároveň odosielaný na server ako súčasť JSON správy.

## 13. Komunikačný protokol

Na prenos dát medzi ESP32 a serverom bol zvolený protokol:

```text
HTTP POST
```

Dôvody výberu:

- jednoduchá implementácia na ESP32
- jednoduché spracovanie vo Flask aplikácii
- vhodné pre REST API architektúru
- jednoduché testovanie pomocou webového prehliadača alebo nástrojov ako curl
- čitateľný formát dát JSON

ESP32 odosiela dáta na endpoint:

```text
POST /api/data
```

Príklad adresy servera:

```text
http://<SERVER_IP>:5000/api/data
```

## 14. Bezpečnosť prenosu

Počas lokálneho testovania prebieha komunikácia medzi ESP32 a Flask serverom pomocou HTTP protokolu v lokálnej sieti. Táto voľba bola zvolená z dôvodu jednoduchosti implementácie a demonštračného charakteru projektu.

Pre verejný prístup k webovému dashboardu je možné použiť ngrok tunel, ktorý poskytuje verejnú HTTPS adresu.

V produkčnom nasadení by bolo vhodné doplniť HTTPS priamo na serverovej strane, autentifikáciu zariadenia a bezpečné uloženie konfiguračných údajov.

## 15. Formát prenášaných dát

Dáta sú prenášané vo formáte JSON.

Príklad správy odosielanej z ESP32:

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

Server doplní časovú pečiatku pri prijatí správy.

## 16. Serverová časť

Serverová časť je implementovaná v jazyku Python pomocou frameworku Flask.

Umiestnenie serverovej časti:

```text
server/app.py
```

Hlavné endpointy:

| Endpoint | Metóda | Popis |
|---|---|---|
| `/` | GET | webový dashboard |
| `/api/data` | POST | príjem dát z ESP32 |
| `/api/latest` | GET | posledné meranie |
| `/api/history` | GET | história meraní |

Server prijíma JSON dáta z ESP32, validuje ich a ukladá do SQLite databázy.

## 17. Databáza

Ako databáza bola zvolená:

```text
SQLite
```

Dôvody výberu:

- jednoduché použitie bez samostatného databázového servera
- vhodná pre menší IoT projekt
- dáta sú uložené lokálne v jednom súbore
- jednoduché nasadenie
- prenositeľnosť projektu

Tabuľka `measurements` obsahuje:

| Stĺpec | Typ | Popis |
|---|---|---|
| id | INTEGER | primárny kľúč |
| temperature | REAL | teplota |
| humidity | REAL | vlhkosť |
| sensor | TEXT | názov snímača |
| unit_temperature | TEXT | jednotka teploty |
| unit_humidity | TEXT | jednotka vlhkosti |
| fan_state | TEXT | stav ventilátora |
| timestamp | TEXT | čas prijatia merania |

Databázový súbor `measurements.db` sa nevkladá do repozitára, pretože vzniká automaticky pri spustení servera.

## 18. Webová vizualizácia

Webové rozhranie zobrazuje:

- aktuálnu teplotu
- aktuálnu vlhkosť
- jednotku meranej veličiny
- názov snímača
- čas posledného merania
- stav ventilátora
- historický graf teploty
- historický graf vlhkosti
- tabuľku posledných meraní

Na vykreslenie grafov je použitá knižnica:

```text
Chart.js
```

Dashboard sa automaticky obnovuje každých 5 sekúnd.

## 19. Historické dáta

Dashboard umožňuje zobrazenie histórie v dvoch režimoch:

1. **Posledných 20 meraní**
2. **Posledných 24 hodín**

Tým je splnená požiadavka na zobrazenie historických dát minimálne za posledných 24 hodín.

Endpoint pre históriu:

```text
GET /api/history?mode=last20
GET /api/history?mode=24h
```

## 20. Dostupnosť webového rozhrania

Webové rozhranie beží lokálne na porte 5000:

```text
http://127.0.0.1:5000/
```

Počas demonštrácie môže byť sprístupnené verejne pomocou tunelového riešenia **ngrok**:

```bash
ngrok http 5000
```

Ngrok vytvorí verejnú HTTPS adresu, cez ktorú je možné dashboard otvoriť aj mimo lokálnej siete.

Príklad:

```text
https://<generated-ngrok-url>.ngrok-free.app
```

Na bezdrôtový prenos dát z ESP32 bol počas testovania použitý iPhone hotspot alebo lokálna Wi-Fi sieť.

## 21. Konfiguračné parametre

Citlivé údaje, ako názov Wi-Fi siete, heslo alebo IP adresa servera, sa nemajú ukladať priamo do verejného repozitára.

Vo firmvéri je potrebné pred nahratím nastaviť:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://YOUR_SERVER_IP:5000/api/data";
```

Reálne heslá a lokálne IP adresy nie sú súčasťou verejného repozitára.

## 22. Inštalácia serverovej časti

### 1. Klonovanie repozitára

```bash
git clone https://github.com/<USERNAME>/<REPOSITORY_NAME>.git
cd <REPOSITORY_NAME>/server
```

### 2. Vytvorenie virtuálneho prostredia

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Inštalácia závislostí

```bash
pip install -r requirements.txt
```

Obsah súboru `requirements.txt`:

```text
Flask
```

### 4. Spustenie servera

```bash
python3 app.py
```

Server bude dostupný na adrese:

```text
http://127.0.0.1:5000/
```

## 23. Nahratie firmvéru do ESP32

### 1. Otvorenie Arduino IDE

V Arduino IDE je potrebné nainštalovať podporu pre ESP32 dosky:

```text
esp32 by Espressif Systems
```

### 2. Výber dosky

V Arduino IDE zvoliť:

```text
Tools → Board → ESP32 Dev Module
```

### 3. Výber portu

Po pripojení ESP32 cez USB-C zvoliť príslušný COM port:

```text
Tools → Port → COMx
```

Ak sa port nezobrazí, je potrebné nainštalovať ovládač pre CP210x USB to UART Bridge.

### 4. Inštalácia knižníc

V Arduino Library Manager je potrebné nainštalovať:

```text
DHT sensor library
Adafruit Unified Sensor
```

### 5. Nastavenie Wi-Fi a servera

Vo firmvéri je potrebné upraviť:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://YOUR_SERVER_IP:5000/api/data";
```

### 6. Nahratie firmvéru

Kliknúť na:

```text
Upload
```

Ak sa nahrávanie zasekne na `Connecting...`, je možné podržať tlačidlo `BOOT` na ESP32, kým sa nezačne zápis firmvéru.

## 24. Spustenie celého systému

Postup spustenia:

1. Pripojiť ESP32 k počítaču alebo napájaniu.
2. Spustiť Flask server:

```bash
python3 app.py
```

3. Otvoriť dashboard:

```text
http://127.0.0.1:5000/
```

4. ESP32 sa pripojí k Wi-Fi a začne odosielať merania.
5. Na dashboarde sa zobrazia aktuálne hodnoty a grafy.
6. Pre verejný prístup je možné spustiť ngrok:

```bash
ngrok http 5000
```



Autor projektu:
Ablazov Yehor


Predmet:
MISA

