# Fluke 435 - Import do Power Log Classic 4.6 a Export do textového súboru

## Prehľad

Tento dokument popisuje proces importu dát z analyzátora kvality energie **Fluke 435** do programu **Power Log Classic 4.6** a následný export dát do textového dokumentu.

---

## 1. Import dát z Fluke 435 do Power Log Classic 4.6

### 1.1 Požiadavky

**Hardvér:**
- Fluke 435 analyzátor kvality energie
- PC s operačným systémom Windows Vista, 7, 8, alebo 10
- Optický kábel OC4USB (RS232) - dodávaný s prístrojom
- Alternatívne: SD karta (odporúčané pre veľké objemy dát)

**Softvér:**
- Power Log Classic 4.6 (alebo kompatibilná verzia)
- **DÔLEŽITÉ**: Verzia firmware prístroja a verzia softvéru Power Log musia byť vzájomne kompatibilné

### 1.2 Metódy pripojenia

#### Metóda A: Optický kábel OC4USB (RS232)

1. **Pripojenie prístroja:**
   - Pripojte optický kábel OC4USB k optickému portu na Fluke 435
   - Pripojte USB koniec kábla k PC
   - Počkajte na inštaláciu ovládačov (ak je potrebné)

2. **Stiahnutie dát v Power Log Classic:**
   - Spustite Power Log Classic 4.6
   - Prejdite do menu alebo použite funkciu pre sťahovanie dát z prístroja
   - Vyberte príslušný COM port
   - Kliknite na "Download" alebo "Import"
   - Po dokončení sťahovania vyberte **"Save Data"** (povinné pre Fluke 434 a 435)

**Poznámka:** Čím viac dát je uložených v analyzátore, tým dlhšie trvá prenos cez USB kábel.

#### Metóda B: SD karta (Odporúčaná)

1. **Export na SD kartu v prístroji:**
   - Vložte SD kartu do Fluke 435
   - V menu prístroja vyberte funkciu pre uloženie/export dát na SD kartu
   - Počkajte na dokončenie exportu
   - Bezpečne vyberte SD kartu

2. **Import zo SD karty:**
   - Vložte SD kartu do čítačky na PC
   - V Power Log Classic otvorte súbory z SD karty
   - Uložte dáta do projektu

**Výhoda:** Podstatne rýchlejší prenos, najmä pri veľkých objemoch nameraných dát.

### 1.3 Kompatibilita

- Power Log Classic je kompatibilný s prístrojmi: Fluke 345, VR1710, 1735, 433, 434, 435
- Softvér funguje na MS Windows NT, 2000, XP, Vista, 7, 8, 10
- **Kritické:** Verzia firmware prístroja musí zodpovedať verzii Power Log Classic softvéru

---

## 2. Export dát z Power Log Classic do textového súboru

### 2.1 Postup exportu

1. **Otvorenie dát:**
   - V Power Log Classic otvorte súbor s nameranými dátami
   - Prejdite do okna "Spreadsheet" (tabuľka)

2. **Výber dát pre export:**
   - Vyberte riadky merania, ktoré chcete exportovať
   - Pre intervalové dáta vyberte:
     - Mesiac
     - Dátum
     - Rok
     - Časové intervaly

3. **Export:**
   - Prejdite do menu **File | Export**
   - Otvorí sa dialóg pre export dát
   - Vyberte požadované parametre a formát
   - Kliknite na **Save** (Uložiť)

4. **Výsledok:**
   - Dáta sa uložia v textovom formáte (TSV - Tab Separated Values)
   - Súbor je kompatibilný s MS Excel a inými tabuľkovými procesormi

### 2.2 Možnosti exportu

Power Log Classic 4.6 obsahuje:
- **Data Export Assistant** - sprievodca exportom (od verzie 4.1)
- Možnosť výberu konkrétnych parametrov merania
- Predvolený formát optimalizovaný pre MS Excel
- Možnosť exportu pre ďalšie spracovanie v iných programoch

---

## 3. Formát exportovaného textového súboru

### 3.1 Všeobecná štruktúra

Exportovaný súbor má formát **TSV (Tab-Separated Values)** s nasledujúcou štruktúrou:

```
Stĺpec 1: Dátum
Stĺpec 2: Čas
Stĺpec 3-N: Parametre merania (Min, Priem, Max)
```

### 3.2 Kódovanie

- **Kódovanie znakov:** Windows-1250 alebo UTF-8 (slovenská lokalizácia)
- **Oddeľovač stĺpcov:** Tabulátor (TAB, \t)
- **Oddeľovač riadkov:** CRLF (\r\n) - Windows štandard
- **Decimálny oddeľovač:** Čiarka (,) - slovenské regionálne nastavenie
- **Oddeľovač tisícov:** Žiadny alebo medzera

### 3.3 Štruktúra hlavičky

Prvý riadok obsahuje názvy parametrov v slovenčine. Príklad:

```
Dátum	Čas	Napätie L1N Min	Napätie L1N Priem	Napätie L1N Max	Napätie L2N Min	...
```

### 3.4 Kategórie meraných parametrov

Exportovaný súbor obsahuje nasledujúce kategórie údajov:

#### A) Časové údaje
- **Dátum** - formát: DD.MM.RRRR
- **Čas** - formát: HH:MM:SS.mmm (s milisekundami)

#### B) Napätie (Voltage)
Pre každú fázu (L1N, L2N, L3N) a neutrál-zem (NG):
- **Napätie Min** - minimálna hodnota
- **Napätie Priem** - priemerná hodnota
- **Napätie Max** - maximálna hodnota
- **Polovičné napätie V RMS** (Min, Priem, Max)
- **Maximálne napätie** (Min, Priem, Max)
- **Napätie Koeficient amplitúdy** (Min, Priem, Max)

#### C) Prúd (Current)
Pre každú fázu (L1, L2, L3) a neutrál (N):
- **Prúd Min, Priem, Max**
- **Polovičný prúd A RMS** (Min, Priem, Max)
- **Maximálny prúd** (Min, Priem, Max)
- **Prúd Koeficient amplitúdy** (Min, Priem, Max)

#### D) Frekvencia
- **Frekvencia Min**
- **Frekvencia Priem**
- **Frekvencia Max**

#### E) Asymetria
- **Asymetria Vn** - napäťová (Min, Priem, Max)
- **Asymetria Vz** - napäťová záporná (Min, Priem, Max)
- **Asymetria An** - prúdová (Min, Priem, Max)
- **Asymetria Az** - prúdová záporná (Min, Priem, Max)

#### F) Výkon
Pre každú fázu a celkový:
- **Činný výkon** (Min, Priem, Max)
- **Klasický VA full** - zdanlivý výkon (Min, Priem, Max)
- **Klasický VAR** - jalový výkon (Min, Priem, Max)

#### G) Power Factor
- **Klasický PF** - Power Factor (Min, Priem, Max)
- **Klasický DPF** - Displacement Power Factor (Min, Priem, Max)

#### H) Harmonické skreslenie
- **THD V** - Total Harmonic Distortion napätia (Min, Priem, Max)
  - Pre L1N, L2N, L3N, NG

#### I) Harmonické zložky (2. až 50. harmonická)
Pre každú harmonickú a každú fázu:
- **Harmonické kmity napätia 2-50** (Min, Priem, Max)
  - Napríklad: "Harmonické kmity napätia2 L1N Min"

#### J) Fázové uhly harmonických
- **Napätie harmonické fázový uhol 1-50** pre L1N, L2N, L3N, NG

### 3.5 Príklad dátového riadku

```
21.10.2025	16:01:00.000	227,108	228,511	229,461	228,619	230,108	...
```

- Dátum: 21. október 2025
- Čas: 16:01:00.000
- Napätie L1N Min: 227,108 V
- Napätie L1N Priem: 228,511 V
- Napätie L1N Max: 229,461 V
- atď.

### 3.6 Špeciálne hodnoty

- **Nulácie:** ,000 (nulové hodnoty)
- **Prázdne hodnoty:** môžu byť reprezentované ako prázdne bunky alebo ,000
- **Chýbajúce merania:** ,000 alebo prázdne pole

---

## 4. Typický workflow

```
┌─────────────────┐
│   Fluke 435     │
│  (meranie dát)  │
└────────┬────────┘
         │
         │ (1) Prenos dát
         │ • Optický kábel OC4USB, alebo
         │ • SD karta
         │
         ▼
┌─────────────────────┐
│ Power Log Classic   │
│      4.6            │
│  (analýza dát)      │
└────────┬────────────┘
         │
         │ (2) Export
         │ File | Export
         │
         ▼
┌─────────────────────┐
│  Textový súbor      │
│  (.txt / .tsv)      │
│  • Tab-separated    │
│  • Excel compatible │
└─────────────────────┘
         │
         │ (3) Ďalšie spracovanie
         │
         ▼
┌─────────────────────┐
│  Excel / Python /   │
│  Iné nástroje       │
└─────────────────────┘
```

---

## 5. Riešenie problémov

### Problém: Prístroj sa nepripojí
**Riešenie:**
- Skontrolujte, či je správne nainštalovaný ovládač pre OC4USB kábel
- Overte správny COM port v Power Log Classic
- Skontrolujte kompatibilitu firmware a softvéru

### Problém: Pomalý prenos dát
**Riešenie:**
- Použite SD kartu namiesto optického kábla
- Vymažte staré dáta z prístroja pred prenosom

### Problém: Exportovaný súbor sa neotvorí v Exceli správne
**Riešenie:**
- Skontrolujte regionálne nastavenia Windows (decimálny oddeľovač)
- V Exceli použijte "Import Data" namiesto priameho otvorenia
- Špecifikujte TAB ako oddeľovač stĺpcov
- Nastavte čiarku ako decimálny oddeľovač

### Problém: Znaky sa zobrazujú nesprávne (�)
**Riešenie:**
- Otvorte súbor s kódovaním Windows-1250 alebo UTF-8
- V Exceli: Data | From Text | File Origin: Windows (Central European)

---

## 6. Poznámky

- Veľkosť exportovaného súboru závisí od množstva zaznamenaných dát
- Pre 24-hodinové meranie s minutovým intervalom: ~1440 riadkov + hlavička
- Jeden záznam môže obsahovať viac ako 2000 parametrov
- Typická veľkosť súboru: 10-20 MB pre 24-hodinové meranie

---

## 7. Súvisiace dokumenty

- Fluke 435 User Manual
- Power Log Classic User Guide
- Power Log Classic Release Notes v4.6

---

**Vytvorené:** 2025-11-12
**Verzia:** 1.0
**Autor:** Claude Code Analysis
