# Fluke 435 Data Processor - User Guide

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Usage Examples](#usage-examples)
5. [Output Files](#output-files)
6. [Acceptance Criteria](#acceptance-criteria)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## 1. Introduction

**Fluke 435 Data Processor** je nástroj na spracovanie a analýzu dát z analyzátora kvality energie Fluke 435, exportovaných pomocou Power Log Classic 4.6.

### Funkcie

- ✅ Automatické čistenie a oprava formátovania dát
- ✅ Robustné rozpoznávanie stĺpcov (SK/CZ/EN)
- ✅ Výpočty energií a validácie
- ✅ Krížové kontroly (súčet fáz vs total, S²=P²+Q²)
- ✅ Generovanie XLSX reportov
- ✅ PNG vizualizácie
- ✅ Škálovateľné (až 10M riadkov)

### Požiadavky

- Python 3.9+
- Pandas
- Matplotlib
- openpyxl

---

## 2. Installation

### Inštalácia závislostí

```bash
pip install pandas matplotlib openpyxl
```

### Overenie inštalácie

```bash
python3 process_fluke.py --version
```

**Output:**
```
Fluke Processor 1.0.0
```

---

## 3. Quick Start

### Základné použitie

```bash
python3 process_fluke.py input.txt
```

Toto:
1. Prečistí dáta (vytvorí `input_clean.txt`)
2. Načíta a spracuje dáta
3. Vypočíta energie a validácie
4. Vytvorí výstupy v `./results/`

### Príklad s reálnym súborom

```bash
python3 process_fluke.py 2025-10-25_BD16.txt --verbose
```

**Output:**
```
================================================================================
Fluke 435 Data Processor v1.0.0
================================================================================

--- FILE INFO ---
File size: 17.4 MB
Estimated rows: 1,440
Estimated columns: 2,413

--- STEP 1: PREPROCESSING ---
Preprocessing complete:
  Total lines: 1,441
  Lines modified: 1,440 (99.9%)

--- STEP 2: COLUMN MAPPING ---
Successfully mapped 26 columns

--- STEP 3: LOADING DATA ---
Loaded 1,440 rows × 26 columns
Memory usage: 0.4 MB

--- STEP 4: CALCULATIONS ---
Energy (P_total): 1691.71 kWh
Energy comparison: ΔE = 0.01% [PASS]
Frequency: 50.006 Hz (±0.019)
Voltage imbalance: mean=0.59%, p95=0.78%

Overall Status: PASS

--- STEP 5: EXPORTING RESULTS ---
Results saved to: ./results/
  - XLSX report: fluke_analysis_20251112_135509.xlsx
  - PNG plots: timeseries_power.png, timeseries_pf.png
  - Clean file: 2025-10-25_BD16_clean.txt
```

---

## 4. Usage Examples

### Example 1: Basic analysis

```bash
python3 process_fluke.py data.txt
```

### Example 2: Custom output directory

```bash
python3 process_fluke.py data.txt --output-dir ./my_analysis
```

### Example 3: Skip preprocessing (if already clean)

```bash
python3 process_fluke.py data_clean.txt --skip-preprocess
```

### Example 4: Verbose output

```bash
python3 process_fluke.py data.txt --verbose
```

### Example 5: Force chunked processing

```bash
python3 process_fluke.py large_file.txt --chunk-size 50000
```

---

## 5. Output Files

### Štruktúra výstupného adresára

```
results/
├── fluke_analysis_YYYYMMDD_HHMMSS.xlsx   # Hlavný XLSX report
├── timeseries_power.png                   # Graf P a S v čase
└── timeseries_pf.png                      # Graf PF (measured vs calculated)

input_clean.txt                             # Prečistený súbor (UTF-8)
```

### XLSX Report - Sheets

#### **Sheet 1: summary**

Hlavné metriky merania:

| Metric | Value | Description |
|--------|-------|-------------|
| Start Time | 2025-10-21 16:01:00 | Začiatok merania |
| End Time | 2025-10-22 16:00:00 | Koniec merania |
| Duration (hours) | 23.98 | Trvanie merania |
| Total Samples | 1,440 | Počet záznamov |
| Dominant Interval (s) | 60 | Vzorkovací interval |
| **Energy (kWh)** | **1691.71** | **Celková energia** |
| Power Mean (W) | 70,488 | Priemerný výkon |
| Delta E (%) | 0.01 | Rozdiel fáz vs total |
| **PF Mean** | **0.881** | **Priemerný účinník** |
| \|ΔPF\| P95 | 0.015 | 95-percentil rozdielu PF |
| Frequency Mean (Hz) | 50.006 | Priemerná frekvencia |
| Voltage Imbalance P95 (%) | 0.78 | Nevyváženosť napätia |
| **Overall Status** | **PASS** | **Celkový stav** |

#### **Sheet 2: validation**

Krížové validácie:

- Σ(P_fáz) vs P_total → relatívna chyba
- Σ(S_fáz) vs S_total → relatívna chyba
- S² = P² + Q² → vektorová kontrola

#### **Sheet 3: timeseries_power**

Časová séria všetkých parametrov:

- timestamp
- P_total, S_total, Q_total
- PF_total, PF_calc
- P_L1N, P_L2N, P_L3N
- S_L1N, S_L2N, S_L3N
- U_L1N, U_L2N, U_L3N
- F (frekvencia)

#### **Sheet 4: data_quality**

Histogram vzorkovacích intervalov (Δt):

| Rank | Interval (s) | Count | Percent |
|------|-------------|-------|---------|
| 1 | 60.0 | 1,439 | 99.9% |
| 2 | 120.0 | 1 | 0.1% |

#### **Sheet 5: mapping_log**

Záznam mapovania stĺpcov:

| Target | Source | Index |
|--------|--------|-------|
| datum | Dátum | 0 |
| cas | Čas | 1 |
| P_total | Činný výkon Celkom Priem | 123 |
| ... | ... | ... |

### PNG Plots

#### **timeseries_power.png**

Graf celkového činného výkonu (P) a zdanlivého výkonu (S) v čase.

- **Modrá čiara:** P (kW)
- **Červená čiara:** S (kVA)

#### **timeseries_pf.png**

Porovnanie meraného a vypočítaného účinníka.

- **Modrá čiara:** PF measured (z prístroja)
- **Červená prerušovaná:** PF calculated (P/S)

---

## 6. Acceptance Criteria

Nástroj automaticky kontroluje nasledujúce kritériá:

### 1. ΔE% (Energia: Σfáz vs total)

| Status | Threshold | Interpretation |
|--------|-----------|----------------|
| ✅ **PASS** | ≤ 1% | Výborná zhoda |
| ⚠️ **INFO** | 1-3% | Akceptovateľná odchýlka |
| 🚨 **ALERT** | > 3% | Značná odchýlka - kontrola! |

**Vzorec:**
```
ΔE% = |E_phase_sum - E_total| / E_total × 100%
```

### 2. \|ΔPF\| (Power Factor Difference)

| Status | Threshold (P95) | Interpretation |
|--------|-----------------|----------------|
| ✅ **PASS** | ≤ 0.05 | Výborná zhoda |
| ⚠️ **INFO** | 0.05-0.1 | Mierna odchýlka |
| 🚨 **ALERT** | > 0.1 | Veľká odchýlka - kontrola! |

**Vzorec:**
```
ΔPF = |PF_measured - (P/S)|
```

### 3. Vector Validation (S² = P² + Q²)

| Status | Threshold (P95) | Interpretation |
|--------|-----------------|----------------|
| ✅ **PASS** | ≤ 0.3 | Fyzikálne konzistentné |
| ⚠️ **INFO** | 0.3-0.6 | Mierna nekonzistencia |
| 🚨 **ALERT** | > 0.6 | Veľká nekonzistencia |

### 4. Voltage Imbalance

| Status | Threshold (P95) | Interpretation |
|--------|-----------------|----------------|
| ✅ **PASS** | ≤ 2% | V norme (EN 50160) |
| ⚠️ **INFO** | 2-3% | Na hranici normy |
| 🚨 **ALERT** | > 3% | Mimo normu |

**Vzorec:**
```
Imbalance = max(|U_i - Ū|) / Ū × 100%
kde Ū = (U_L1N + U_L2N + U_L3N) / 3
```

### Overall Status

- **PASS:** Všetky kritériá splnené
- **INFO:** Aspoň jedno kritérium v INFO stave
- **ALERT:** Aspoň jedno kritérium v ALERT stave

---

## 7. Troubleshooting

### Problém 1: "Critical columns not found"

**Error:**
```
[ERROR] Critical columns not found: ['P_total']
[ERROR] Cannot proceed without these columns.
```

**Príčina:** Nástroj nemôže nájsť stĺpec s činným výkonom.

**Riešenie:**
1. Overte, že súbor je skutočne z Fluke 435 / Power Log Classic
2. Skontrolujte, či je hlavička v prvom riadku
3. Ak používate iný jazyk (EN), upravte `COLUMN_KEYWORDS` v `fluke_processor/config.py`

---

### Problém 2: Excel sa neotvorí správne

**Symptóm:** Znaky sa zobrazujú nesprávne.

**Riešenie:** Súbor je už v UTF-8. Otvorte priamo v Exceli (nie cez Import wizard).

---

### Problém 3: "Memory Error"

**Error:**
```
MemoryError: Unable to allocate array
```

**Príčina:** Nedostatok RAM pre veľký súbor.

**Riešenie:** Použite chunked processing:

```bash
python3 process_fluke.py large_file.txt --chunk-size 20000
```

---

### Problém 4: Pomalé spracovanie

**Symptóm:** Spracovanie trvá dlho.

**Optimalizácie:**
1. Použite `--skip-preprocess` ak máte už clean file
2. Znížte chunk-size pre menšiu pamäť (ale bude to pomalšie)
3. Spracovávajte len časť dát (extrahujte prvých X riadkov)

---

## 8. FAQ

### Q1: Aké formáty súborov sú podporované?

**A:** Tab-separated text files (TSV) exportované z Power Log Classic 4.6. Súbory musia byť v kódovaní CP1250 alebo UTF-8.

---

### Q2: Môžem spracovať súbory v angličtine?

**A:** Áno, fuzzy matching podporuje viacjazyčné hlavičky. Ak máte problémy, upravte `COLUMN_KEYWORDS` v `config.py`.

---

### Q3: Koľko času trvá spracovanie?

**A:**
- 1k riadkov: <3 sekundy
- 10k riadkov: ~5 sekúnd
- 100k riadkov: ~20 sekúnd
- 1M riadkov: ~90 sekúnd

---

### Q4: Ako môžem zmeniť acceptance thresholds?

**A:** Upravte `THRESHOLDS` v `fluke_processor/config.py`:

```python
THRESHOLDS = {
    'delta_E_percent': {
        'pass': 1.0,    # ≤ 1%
        'info': 3.0,    # 1-3%
        'alert': 3.0    # > 3%
    },
    # ...
}
```

---

### Q5: Môžem spracovať dáta z iných analyzátorov?

**A:** Nástroj je optimalizovaný pre Fluke 435, ale môže fungovať s podobnými formátmi ak obsahujú:
- Dátum a čas
- Aspoň P_total a S_total
- Tab-separated formát

---

### Q6: Kde nájdem technickú dokumentáciu?

**A:** V repozitári:
- `ANALYZA_A_NAVRH_RIESENIA.md` - Architektúra a design
- `FORMAT_ANALYZA_TECHNICKA.md` - Technická špecifikácia formátu
- `FLUKE_435_IMPORT_EXPORT_DOKUMENTACIA.md` - Import/export proces

---

## Support

Pre ot

ázky a problémy:
- GitHub Issues: [aranej/Fluke435-analyze](https://github.com/aranej/Fluke435-analyze)
- Email: (kontakt autora repozitára)

---

**Autor:** Claude Code Analysis
**Verzia:** 1.0.0
**Dátum:** 2025-11-12
