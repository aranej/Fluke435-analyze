# Technická analýza formátu exportovaného súboru Fluke 435

## Základné informácie o súbore

**Analyzovaný súbor:** `2025-10-25_BD16.txt`
**Veľkosť súboru:** 18 290 371 bajtov (~ 17.4 MB)
**Počet riadkov:** 1 440 (vrátane hlavičky)
**Počet stĺpcov:** 2 414
**Formát:** TSV (Tab-Separated Values)

## Štruktúra súboru

### 1. Kódovanie a oddeľovače

```
Kódovanie znakov:    Windows-1250 (Central European)
Oddeľovač stĺpcov:   TAB (\t, 0x09)
Oddeľovač riadkov:   CRLF (\r\n, 0x0D 0x0A)
Decimálny oddeľovač: Čiarka (,)
Oddeľovač tisícov:   Žiadny
```

### 2. Časové údaje (Stĺpce 1-2)

| Stĺpec | Názov | Formát | Príklad |
|--------|-------|--------|---------|
| 1 | Dátum | DD.MM.RRRR | 21.10.2025 |
| 2 | Čas | HH:MM:SS.mmm | 16:01:00.000 |

**Časový interval medzi záznamami:** 1 minúta
**Časové rozpätie v súbore:** 24 hodín (21.10.2025 16:01 - 22.10.2025 16:00)

### 3. Kategórie meraných parametrov

#### A) Napätie - Stĺpce 3-50 (48 stĺpcov)

**Fázy:** L1N, L2N, L3N, NG (Neutral-Ground)
**Typy merania:**
- Napätie (Min, Priem, Max) - základné meranie
- Polovičné napätie V RMS (Min, Priem, Max) - polovičná perióda
- Maximálne napätie (Min, Priem, Max) - peak hodnoty
- Napätie Koeficient amplitúdy (Min, Priem, Max) - crest factor

**Štruktúra:**
```
Stĺpec  3: Napätie L1N Min
Stĺpec  4: Napätie L1N Priem
Stĺpec  5: Napätie L1N Max
...
Stĺpec 48: Napätie NG Priem
Stĺpec 49: Napätie NG Max
Stĺpec 50: Napätie Koeficient amplitúdy NG Max
```

**Jednotky:** Volty (V)
**Typický rozsah:** 220-240 V (pre L1N, L2N, L3N), 0-5 V (pre NG)

#### B) Prúd - Stĺpce 51-98 (48 stĺpcov)

**Fázy:** L1, L2, L3, N (Neutral)
**Typy merania:**
- Prúd (Min, Priem, Max) - základné meranie
- Polovičný prúd A RMS (Min, Priem, Max)
- Maximálny prúd (Min, Priem, Max)
- Prúd Koeficient amplitúdy (Min, Priem, Max)

**Štruktúra:**
```
Stĺpec 51: Prúd L1 Min
Stĺpec 52: Prúd L1 Priem
Stĺpec 53: Prúd L1 Max
...
Stĺpec 98: Prúd Koeficient amplitúdy N Max
```

**Jednotky:** Ampéry (A)
**Typický rozsah:** Závisí od meranej záťaže (v príklade: 120-180 A)

#### C) Frekvencia - Stĺpce 99-101 (3 stĺpce)

```
Stĺpec  99: Frekvencia Min
Stĺpec 100: Frekvencia Priem
Stĺpec 101: Frekvencia Max
```

**Jednotky:** Hertz (Hz)
**Typický rozsah:** 49.9-50.1 Hz (európska sieť)

#### D) Asymetria - Stĺpce 102-113 (12 stĺpcov)

**Typy:**
- Asymetria Vn - napäťová nesymetria (negative sequence)
- Asymetria Vz - napäťová zero sequence
- Asymetria An - prúdová nesymetria
- Asymetria Az - prúdová zero sequence

```
Stĺpec 102: Asymetria Vn Min
Stĺpec 103: Asymetria Vn Priem
Stĺpec 104: Asymetria Vn Max
...
Stĺpec 113: Asymetria Az Max
```

**Jednotky:** Percentá (%)

#### E) Výkon - Stĺpce 114-149 (36 stĺpcov)

**Kategórie výkonu:**
1. **Činný výkon (W)** - L1N, L2N, L3N, Celkom
2. **Klasický VA full** - zdanlivý výkon (VA)
3. **Klasický VAR** - jalový výkon (VAR)

Pre každú kategóriu: Min, Priem, Max

```
Stĺpec 114: Činný výkon L1N Min
Stĺpec 115: Činný výkon L1N Priem
Stĺpec 116: Činný výkon L1N Max
...
Stĺpec 149: Klasický VAR Celkom Max
```

**Jednotky:**
- W (watty) pre činný výkon
- VA (voltampéry) pre zdanlivý výkon
- VAR (voltampére reaktívne) pre jalový výkon

**Typický rozsah:** V analyzovanom súbore: 20-40 kW

#### F) Power Factor - Stĺpce 150-173 (24 stĺpcov)

**Typy:**
1. **Klasický PF** - Power Factor
2. **Klasický DPF** - Displacement Power Factor

Pre každú fázu (L1N, L2N, L3N) a Celkom: Min, Priem, Max

```
Stĺpec 150: Klasický PF L1N Min
Stĺpec 151: Klasický PF L1N Priem
Stĺpec 152: Klasický PF L1N Max
...
Stĺpec 173: Klasický DPF Celkom Max
```

**Jednotky:** Bezrozmerné (0-1)
**Typický rozsah:** 0.80-0.95

#### G) THD (Total Harmonic Distortion) - Stĺpce 174-185 (12 stĺpcov)

Pre každú fázu (L1N, L2N, L3N, NG): Min, Priem, Max

```
Stĺpec 174: THD V L1N Min
Stĺpec 175: THD V L1N Priem
Stĺpec 176: THD V L1N Max
...
Stĺpec 185: THD V NG Max
```

**Jednotky:** Percentá (%)
**Typický rozsah:** 0-10% (dobrá kvalita siete)

#### H) Harmonické zložky 2-50 - Stĺpce 186-1773 (1588 stĺpcov)

**Počet harmonických:** 49 (od 2. do 50. harmonickej)
**Pre každú harmonickú:**
- 4 fázy (L1N, L2N, L3N, NG)
- 3 hodnoty (Min, Priem, Max)
- Spolu: 49 × 4 × 3 = 588 stĺpcov

**Vzorec pre výpočet čísla stĺpca:**
```
Harmonická N, Fáza F, Typ T:
Stĺpec = 186 + (N-2) × 12 + F × 3 + T

kde:
N = číslo harmonickej (2-50)
F = fáza (0=L1N, 1=L2N, 2=L3N, 3=NG)
T = typ (0=Min, 1=Priem, 2=Max)
```

**Príklady:**
```
Stĺpec 186: Harmonické kmity napätia2 L1N Min     (2. harmonická, L1N, Min)
Stĺpec 187: Harmonické kmity napätia2 L1N Priem   (2. harmonická, L1N, Priem)
Stĺpec 188: Harmonické kmity napätia2 L1N Max     (2. harmonická, L1N, Max)
...
Stĺpec 762: Harmonické kmity napätia50 L1N Min    (50. harmonická, L1N, Min)
Stĺpec 773: Harmonické kmity napätia50 NG Max     (50. harmonická, NG, Max)
```

**Jednotky:** Percentá (%) - relatívne k základnej harmonickej

#### I) Fázové uhly harmonických 1-50 - Stĺpce 1774-2414 (641 stĺpcov)

Pre každú harmonickú (1-50) a každú fázu (L1N, L2N, L3N, NG):
- Len jedna hodnota (okamžitá)
- Spolu: 50 × 4 = 200 hodnôt platných údajov
- Ostatné hodnoty sú prázdne (nuly)

**Vzorec pre výpočet:**
```
Harmonická N, Fáza F:
Stĺpec = 1774 + (N-1) × 4 + F

kde:
N = číslo harmonickej (1-50)
F = fáza (0=L1N, 1=L2N, 2=L3N, 3=NG)
```

**Príklady:**
```
Stĺpec 1774: Napätie harmonické fázový uhol1 L1N  (1. harmonická, L1N)
Stĺpec 1775: Napätie harmonické fázový uhol1 L2N  (1. harmonická, L2N)
Stĺpec 1776: Napätie harmonické fázový uhol1 L3N  (1. harmonická, L3N)
Stĺpec 1777: Napätie harmonické fázový uhol1 NG   (1. harmonická, NG)
...
Stĺpec 2410: Napätie harmonické fázový uhol50 L2N (50. harmonická, L2N)
Stĺpec 2411: Napätie harmonické fázový uhol50 L3N (50. harmonická, L3N)
Stĺpec 2412: Napätie harmonické fázový uhol50 NG  (50. harmonická, NG)
```

**Jednotky:** Stupne (°)
**Rozsah:** 0-360°

**Poznámka:** Posledné stĺpce (2413-2414) sú pravdepodobne reserve alebo checksum údaje.

## 4. Formát hodnôt

### Decimálne čísla
```
Formát:         ###,###
Decimály:       3 miesta
Príklady:       227,108
                1,450
                49,999
```

### Špeciálne hodnoty
```
Nula:           ,000
Veľmi malá:     ,010
Prázdna:        (prázdne pole alebo ,000)
Negatívna:      -18881,213
```

### Exponenty
Nie sú používané, všetky hodnoty sú v desiatkovom formáte.

## 5. Príklad dátového riadku

```tsv
21.10.2025	16:01:00.000	227,108	228,511	229,461	...	0,000	0,000
```

Rozdelené:
- **Dátum:** 21.10.2025
- **Čas:** 16:01:00.000
- **Napätie L1N Min:** 227,108 V
- **Napätie L1N Priem:** 228,511 V
- **Napätie L1N Max:** 229,461 V
- ...
- **(posledné stĺpce):** 0,000

## 6. Štatistika súboru

```
Celkový počet údajov:        1,439 riadkov × 2,414 stĺpcov = 3,472,546 hodnôt
Časové rozpätie:             24 hodín (1440 minút)
Interval záznamu:            1 minúta
Veľkosť súboru:              18.3 MB
Priemerna veľkosť riadku:    ~12.7 kB
```

## 7. Programatické spracovanie

### Python - Pandas

```python
import pandas as pd

# Načítanie súboru s správnym kódovaním
df = pd.read_csv(
    '2025-10-25_BD16.txt',
    sep='\t',
    encoding='windows-1250',
    decimal=',',
    thousands=''
)

# Konverzia dátumu a času
df['Dátum_Čas'] = pd.to_datetime(
    df['Dátum'] + ' ' + df['Čas'],
    format='%d.%m.%Y %H:%M:%S.%f'
)

# Prístup k dátam
voltage_l1n_avg = df['Napätie L1N Priem']
current_l1_avg = df['Prúd L1 Priem']
power_total = df['Činný výkon Celkom Priem']

# Export do CSV s anglickými nastaveniami
df.to_csv(
    'output.csv',
    sep=',',
    decimal='.',
    encoding='utf-8',
    index=False
)
```

### Python - CSV modul

```python
import csv
from datetime import datetime

with open('2025-10-25_BD16.txt', 'r', encoding='windows-1250') as f:
    reader = csv.reader(f, delimiter='\t')

    # Prečítaj hlavičku
    header = next(reader)

    # Spracuj dáta
    for row in reader:
        date_str = row[0]  # Dátum
        time_str = row[1]  # Čas

        # Konverzia hodnôt - nahraď čiarku bodkou
        voltage_l1n_min = float(row[2].replace(',', '.'))
        voltage_l1n_avg = float(row[3].replace(',', '.'))

        # Spracovanie...
```

### Excel - Import

1. **Otvorte Excel**
2. **Data → From Text/CSV**
3. **Nastavenia:**
   - File Origin: `Windows (Central European) - 1250`
   - Delimiter: `Tab`
   - Data Type Detection: Based on entire dataset
4. **Transform Data:**
   - Nahraďte čiarky bodkami (Find & Replace): `,` → `.`
   - Konvertujte stĺpce na čísla

### Excel - Alternatívny import

1. **Data → Get Data → From File → From Text/CSV**
2. **Power Query Editor:**
```powerquery
= Csv.Document(
    File.Contents("2025-10-25_BD16.txt"),
    [
        Delimiter=#(tab),
        Encoding=1250,
        Columns=2414
    ]
)
```

## 8. Možné problémy a riešenia

### Problém 1: Nesprávne zobrazenie diakritiky
**Symptóm:** Znaky `�` namiesto `á`, `č`, atď.
**Riešenie:** Použite kódovanie `windows-1250` alebo `iso-8859-2`

### Problém 2: Čísla sa načítavajú ako text
**Symptóm:** Nemožno vykonať matematické operácie
**Riešenie:**
```python
# Nahraďte čiarky bodkami pred konverziou
df = df.replace(',', '.', regex=True)
df = df.apply(pd.to_numeric, errors='ignore')
```

### Problém 3: Príliš veľa stĺpcov pre Excel
**Symptóm:** Excel má limit 16,384 stĺpcov
**Riešenie:**
- Importujte len potrebné stĺpce
- Použite Python/R pre analýzu
- Rozdeľte súbor na viacero častí

### Problém 4: Pamäťové nároky
**Symptóm:** Nedostatok RAM pri načítaní
**Riešenie:**
```python
# Načítavajte po častiach (chunks)
chunk_iter = pd.read_csv(
    '2025-10-25_BD16.txt',
    sep='\t',
    encoding='windows-1250',
    decimal=',',
    chunksize=100  # 100 riadkov naraz
)

for chunk in chunk_iter:
    # Spracujte chunk
    process(chunk)
```

## 9. Užitočné skripty

### Získanie zoznamu stĺpcov
```bash
head -1 2025-10-25_BD16.txt | tr '\t' '\n' > columns.txt
```

### Počet riadkov
```bash
wc -l 2025-10-25_BD16.txt
```

### Extrakcia špecifických stĺpcov (napríklad 1,2,3,4,5)
```bash
cut -f1,2,3,4,5 2025-10-25_BD16.txt > extract.txt
```

### Konverzia na CSV s bodkou
```bash
sed 's/,/./g' 2025-10-25_BD16.txt | sed 's/\t/,/g' > output.csv
```

## 10. Zhrnutie - Quick Reference

| Parameter | Hodnota |
|-----------|---------|
| **Formát** | TSV |
| **Kódovanie** | Windows-1250 |
| **Oddeľovač stĺpcov** | TAB (\t) |
| **Oddeľovač riadkov** | CRLF (\r\n) |
| **Decimálny oddeľovač** | Čiarka (,) |
| **Počet stĺpcov** | 2 414 |
| **Počet riadkov** | 1 440 (vrátane hlavičky) |
| **Časový interval** | 1 minúta |
| **Veľkosť súboru** | ~18 MB |

---

**Vytvorené:** 2025-11-12
**Verzia:** 1.0
**Autor:** Claude Code Analysis
