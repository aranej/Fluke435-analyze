# Analýza a návrh riešenia: Fluke 435 Data Processor

## 📋 Executive Summary

Po dôkladnej analýze Fluke 435 exportovaných dát a špecifikácie požiadaviek odporúčam **modulárny prístup s tromi hlavnými komponentmi**:

1. **Data Preprocessor** - Čistenie a normalizácia dát
2. **Core Processor** - Výpočty a validácie
3. **Report Generator** - XLSX + PNG výstupy

**Kľúčové zistenia:**
- ✅ Fuzzy matching hlavičiek funguje výborne
- ⚠️ Pandas vyžaduje špeciálne nastavenia pre decimal/thousands
- ⚠️ Súbor obsahuje 2413 stĺpcov (1588 harmonických = 66% dát)
- ✅ Chunking nie je potrebný pre <10M riadkov ak použijeme selective loading

---

## 🔍 1. Analýza existujúcich dát

### 1.1 Štruktúra súboru

```
Súbor: 2025-10-25_BD16.txt
Veľkosť: 17.4 MB
Riadkov: 1,440 (24 hodín × 1 minúta)
Stĺpcov: 2,413
Kódovanie: CP1250 (Windows Central European)
```

**Rozdelenie stĺpcov:**
| Kategória | Počet | Podiel | Dôležitosť |
|-----------|-------|--------|------------|
| Výkon (P/S/Q/PF) | 672 | 27.9% | ⭐⭐⭐ Kritické |
| Prúd | 836 | 34.7% | ⭐⭐ Vysoká |
| Harmonické 2-50 | 588 | 24.4% | ⭐ Nízka (optional) |
| Napätie | 248 | 10.3% | ⭐⭐ Stredná |
| THD | 33 | 1.4% | ⭐ Nízka |
| Ostatné | 36 | 1.5% | ⭐ Nízka |

**Memory footprint:**
```
Všetky stĺpce:  ~27 MB (pre 1k riadkov) → 27 GB (pre 1M riadkov) ❌
Core stĺpce:     ~0.2 MB (pre 1k riadkov) → 200 MB (pre 1M riadkov) ✅
```

### 1.2 Identifikované problémy vo formáte

```python
Problém                          Výskyt    Príklad              Fix
─────────────────────────────────────────────────────────────────────────
1. Chýbajúca nula pred čiarkou   100%      ",870"             → "0,870"
2. Negatívna bez nuly            100%      "-,123"            → "-0,123"
3. Prázdne hodnoty (tab-tab)     100%      "...\t\t..."       → "...\t0,0\t..."
4. Pandas thousands separator    N/A       "83616,805" → 83.6 → thousands=''
```

### 1.3 Overený mapping kľúčových stĺpcov

| Parameter | Index | Pôvodný názov | Príklad hodnoty |
|-----------|-------|---------------|-----------------|
| Dátum | 0 | "Dátum" | 21.10.2025 |
| Čas | 1 | "Čas" | 16:01:00.000 |
| P_total | 123 | "Činný výkon Celkom Priem" | 83616,805 W |
| S_total | 135 | "Klasický VA full Celkom Priem" | 97103,383 VA |
| Q_total | 147 | "Klasický VAR Celkom Priem" | -51249,008 VAR |
| PF_total | 159 | "Klasický PF Celkom Priem" | ,870 |
| U_L1N | 3 | "Napätie L1N Priem" | 228,511 V |
| U_L2N | 6 | "Napätie L2N Priem" | 230,108 V |
| U_L3N | 9 | "Napätie L3N Priem" | 231,403 V |
| Freq | 100 | "Frekvencia Priem" | 49,999 Hz |

---

## 🏗️ 2. Návrh architektúry

### 2.1 Prístup 1: Monolitický (Single-Pass)

```python
┌─────────────┐
│  Raw TXT    │ (CP1250, 2413 cols)
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Preprocess         │
│  - Fix encoding     │
│  - Fix ,/- values   │
│  - Clean TXT export │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Selective Load     │
│  - Core ~20 cols    │
│  - Optional: phases │
│  - Skip harmonics   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Compute & Validate │
│  - Energy calc      │
│  - Cross-checks     │
│  - Quality metrics  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Export             │
│  - XLSX (5 sheets)  │
│  - PNG (2 plots)    │
└─────────────────────┘
```

**Výhody:**
- ✅ Jednoduchý na implementáciu
- ✅ Rýchly pre súbory <100k riadkov
- ✅ Jeden priechod dátami

**Nevýhody:**
- ❌ Zlá škálovateľnosť pre 10M riadkov
- ❌ Vysoká pamäťová náročnosť

### 2.2 Prístup 2: Chunked Processing (Odporúčané)

```python
┌─────────────┐
│  Raw TXT    │
└──────┬──────┘
       │
       ▼
┌───────────────────────┐
│  Preprocess Stream    │ ← Read line-by-line
│  - Fix on-the-fly     │   Write to clean.txt
│  - Regex substitution │
└──────┬────────────────┘
       │
       ▼
┌───────────────────────┐
│  Chunked Reader       │
│  ┌─────────────────┐  │
│  │ Chunk 1 (20k)   │  │ ← Load selective columns
│  ├─────────────────┤  │
│  │ Chunk 2 (20k)   │  │
│  ├─────────────────┤  │
│  │ Chunk 3 (20k)   │  │
│  └─────────────────┘  │
└──────┬────────────────┘
       │
       ▼
┌───────────────────────┐
│  Aggregate Results    │
│  - Concatenate chunks │
│  - Sort by timestamp  │
│  - Compute metrics    │
└──────┬────────────────┘
       │
       ▼
┌───────────────────────┐
│  Export               │
└───────────────────────┘
```

**Výhody:**
- ✅ Škáluje na 10M+ riadkov
- ✅ Konštantná pamäť (~200 MB)
- ✅ Preprocessing on-the-fly

**Nevýhody:**
- ❌ Komplexnejší kód
- ❌ O niečo pomalší (ale stále <1 min pre 1M riadkov)

### 2.3 Prístup 3: Hybrid (Najlepší kompromis)

```python
if file_size < 100_MB or row_count < 100_000:
    use_single_pass()  # Rýchle
else:
    use_chunked()      # Škálovateľné
```

**Výhody:**
- ✅ Optimálny výkon pre malé súbory
- ✅ Škáluje pre veľké súbory
- ✅ Automatická detekcia

---

## 🚀 3. Implementačné odporúčania

### 3.1 Preprocessing - Regex Substitutions

**Problém:** Pandas nesprávne parsuje hodnoty

**Riešenie:** Preprocess súbor pred načítaním

```python
import re

def preprocess_line(line: str) -> str:
    """Fix common formatting issues"""

    # 1. Fix  \-  →  -
    line = line.replace(' \\- ', '-')
    line = line.replace('\\-', '-')

    # 2. Fix  -,XXX  →  -0,XXX  (negative missing zero)
    line = re.sub(r'(^|\t)-,', r'\1-0,', line)

    # 3. Fix  ,XXX  →  0,XXX  (positive missing zero)
    line = re.sub(r'(^|\t),', r'\10,', line)

    # 4. Fix empty values  \t\t  →  \t0,0\t
    line = re.sub(r'\t\t', '\t0,0\t', line)

    return line

def preprocess_file(input_path: str, output_path: str):
    """Create clean UTF-8 copy with fixes applied"""

    with open(input_path, 'r', encoding='cp1250', errors='replace') as fin:
        with open(output_path, 'w', encoding='utf-8') as fout:

            for line in fin:
                clean_line = preprocess_line(line)
                fout.write(clean_line)
```

**Výhoda:** Jednorázové spustenie, potom pracuješ s čistým súborom

### 3.2 Fuzzy Matching hlavičiek

```python
import unicodedata
import re
from typing import Optional, List

def remove_diacritics(text: str) -> str:
    """Remove diacritics from text"""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def normalize_header(text: str) -> str:
    """Normalize header for fuzzy matching"""
    text = remove_diacritics(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Unify phase notation
    text = text.replace('l1 n', 'l1n')
    text = text.replace('l2 n', 'l2n')
    text = text.replace('l3 n', 'l3n')
    return text

def find_column(columns: List[str], keywords: List[str],
                prefer: List[str] = ['priem', 'avg']) -> Optional[int]:
    """
    Find column by fuzzy matching keywords

    Args:
        columns: List of column names
        keywords: Required keywords (all must match)
        prefer: Preferred aggregation (try in order)

    Returns:
        Column index or None if not found
    """

    candidates = []

    for i, col in enumerate(columns):
        norm = normalize_header(col)

        # All keywords must be present
        if all(kw in norm for kw in keywords):

            # Score by preference
            score = 0
            for j, pref in enumerate(prefer):
                if pref in norm:
                    score = len(prefer) - j  # Higher = better
                    break

            candidates.append((score, i, col))

    if not candidates:
        return None

    # Sort by score (highest first), then by index (lowest first)
    candidates.sort(key=lambda x: (-x[0], x[1]))

    return candidates[0][1]  # Return index

# Usage
columns = load_header('2025-10-25_BD16.txt')

P_total_idx = find_column(columns, ['cinny', 'vykon', 'celkom'])
S_total_idx = find_column(columns, ['va', 'full', 'celkom'])
Q_total_idx = find_column(columns, ['var', 'celkom'])
PF_total_idx = find_column(columns, ['pf', 'celkom'])

# Per-phase
P_L1N_idx = find_column(columns, ['cinny', 'vykon', 'l1n'])
P_L2N_idx = find_column(columns, ['cinny', 'vykon', 'l2n'])
P_L3N_idx = find_column(columns, ['cinny', 'vykon', 'l3n'])
```

### 3.3 Pandas Loading (Správne nastavenia)

```python
import pandas as pd

def load_data_correct(filepath: str,
                      use_cols: List[int],
                      chunksize: Optional[int] = None) -> pd.DataFrame:
    """
    Load data with correct settings for Fluke format

    CRITICAL SETTINGS:
    - decimal=','        # Decimal separator is COMMA
    - thousands=''       # NO thousands separator (not comma!)
    - encoding='utf-8'   # After preprocessing
    """

    if chunksize is None:
        # Single-pass
        df = pd.read_csv(
            filepath,
            sep='\t',
            encoding='utf-8',
            decimal=',',
            thousands='',  # ← CRITICAL!
            usecols=use_cols,
            on_bad_lines='skip',
            low_memory=False
        )
        return df

    else:
        # Chunked
        chunks = []

        reader = pd.read_csv(
            filepath,
            sep='\t',
            encoding='utf-8',
            decimal=',',
            thousands='',
            usecols=use_cols,
            on_bad_lines='skip',
            chunksize=chunksize,
            low_memory=False
        )

        for chunk in reader:
            chunks.append(chunk)

        return pd.concat(chunks, ignore_index=True)
```

### 3.4 Energy Calculation

```python
import numpy as np

def calculate_energy(df: pd.DataFrame,
                     P_col: str = 'P_total') -> dict:
    """
    Calculate energy with adaptive Δt

    Returns:
        {
            'E_kWh': float,           # Total energy
            'dt_mode': float,         # Dominant Δt in seconds
            'dt_histogram': dict,     # Top 3 intervals
            'mixed_sampling': bool    # Flag if multiple Δt values
        }
    """

    # Compute Δt
    df['dt'] = df['timestamp'].diff().dt.total_seconds()

    # Find dominant Δt (mode)
    dt_counts = df['dt'].value_counts()
    dt_mode = dt_counts.index[0]

    # Check for mixed sampling
    top3 = dt_counts.head(3)
    mixed = (top3.iloc[0] / len(df) < 0.95)  # <95% dominant

    # Calculate energy
    dt_h = dt_mode / 3600
    E_kWh = df[P_col].sum() * dt_h / 1000

    return {
        'E_kWh': E_kWh,
        'dt_mode': dt_mode,
        'dt_histogram': dict(top3),
        'mixed_sampling': mixed
    }
```

### 3.5 Cross-Validation

```python
def validate_power_balance(df: pd.DataFrame,
                          P_cols: List[str],
                          S_cols: List[str],
                          Q_cols: List[str]) -> dict:
    """
    Cross-validate power measurements

    Returns metrics with percentiles
    """

    # Sum of phases
    df['P_sum'] = df[P_cols].sum(axis=1)
    df['S_sum'] = df[S_cols].sum(axis=1)
    df['Q_sum'] = df[Q_cols].sum(axis=1) if Q_cols else np.nan

    # Relative errors
    df['P_rel_err'] = np.abs(df['P_sum'] - df['P_total']) / np.abs(df['P_total'] + 1e-6)
    df['S_rel_err'] = np.abs(df['S_sum'] - df['S_total']) / np.abs(df['S_total'] + 1e-6)

    # Vectorova kontrola: S² = P² + Q² (len kde Q existuje)
    if 'Q_total' in df.columns:
        df['S_squared_calc'] = np.sqrt(df['P_total']**2 + df['Q_total']**2)
        df['S_vec_err'] = np.abs(df['S_total'] - df['S_squared_calc']) / df['S_total']

    # PF vypočítaný
    df['PF_calc'] = np.clip(df['P_total'] / (df['S_total'] + 1e-6), -1, 1)
    df['PF_diff'] = np.abs(df['PF_total'] - df['PF_calc'])

    return {
        'P_rel_err_mean': df['P_rel_err'].mean(),
        'P_rel_err_p95': df['P_rel_err'].quantile(0.95),
        'S_rel_err_mean': df['S_rel_err'].mean(),
        'S_rel_err_p95': df['S_rel_err'].quantile(0.95),
        'PF_diff_mean': df['PF_diff'].mean(),
        'PF_diff_p95': df['PF_diff'].quantile(0.95),
        'S_vec_err_p95': df.get('S_vec_err', pd.Series([np.nan])).quantile(0.95)
    }
```

---

## 📊 4. Output Specification

### 4.1 XLSX Sheets

```python
# Sheet 1: summary
{
    'Measurement_Start': '2025-10-21 16:01:00',
    'Measurement_End': '2025-10-22 16:00:00',
    'Duration_hours': 23.98,
    'Sampling_Interval_s': 60,
    'Total_Samples': 1440,
    'Bad_Lines_Skipped': 0,

    'E_total_kWh': 5.44,
    'E_phase_sum_kWh': 5.42,
    'Delta_E_percent': 0.37,

    'PF_mean': 0.881,
    'PF_diff_mean': 0.003,
    'PF_diff_p95': 0.008,

    'S_vec_err_p95': 0.15,

    'Freq_mean_Hz': 50.01,
    'Freq_min_Hz': 49.93,
    'Freq_max_Hz': 50.05,

    'Voltage_Imbalance_p95_percent': 1.2,

    'Status': 'PASS'  # or 'INFO' or 'ALERT'
}

# Sheet 2: validation
{
    'P_phases_vs_total_mean_rel': 0.002,
    'P_phases_vs_total_p95': 0.005,
    'S_phases_vs_total_mean_rel': 0.003,
    ...
}

# Sheet 3: timeseries_power
columns = ['timestamp', 'P_total', 'S_total', 'Q_total', 'PF_total', 'PF_calc',
           'P_L1N', 'P_L2N', 'P_L3N', 'S_L1N', 'S_L2N', 'S_L3N',
           'U_L1N', 'U_L2N', 'U_L3N', 'F']

# Sheet 4: data_quality
{
    'dt_interval_s': [60, 120, 59],
    'count': [1439, 5, 2],
    'percent': [99.9, 0.3, 0.1]
}

# Sheet 5: mapping_log
{
    'Target_Column': ['P_total', 'S_total', ...],
    'Source_Column': ['Činný výkon Celkom Priem', 'Klasický VA full...', ...],
    'Index': [123, 135, ...]
}
```

### 4.2 PNG Plots

```python
import matplotlib.pyplot as plt

# Plot 1: Power timeseries
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df['timestamp'], df['P_total'] / 1000, label='P (kW)', linewidth=1)
ax.plot(df['timestamp'], df['S_total'] / 1000, label='S (kVA)', linewidth=1, alpha=0.7)
ax.set_xlabel('Time')
ax.set_ylabel('Power [kW / kVA]')
ax.legend()
ax.grid(True, alpha=0.3)
plt.savefig('timeseries_power.png', dpi=150, bbox_inches='tight')

# Plot 2: Power Factor
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df['timestamp'], df['PF_total'], label='PF measured', linewidth=1)
ax.plot(df['timestamp'], df['PF_calc'], label='PF calculated', linewidth=1, linestyle='--')
ax.set_xlabel('Time')
ax.set_ylabel('Power Factor')
ax.set_ylim([0, 1])
ax.legend()
ax.grid(True, alpha=0.3)
plt.savefig('timeseries_pf.png', dpi=150, bbox_inches='tight')
```

---

## ⚠️ 5. Kritické výzvy a riešenia

### 5.1 Harmonické vlny (Memory Bomb)

**Problém:**
- 1588 stĺpcov (66% súboru!)
- Pre 1M riadkov = 12.7 GB RAM

**Riešenia:**
1. **Ignorovať pri core processing** ✅ Odporúčané
2. **Optional flag `--include-harmonics`** pre detailnú analýzu
3. **Separate processing** - spracuj harmonické osobitne ak potrebné

```python
# Core processing
core_cols = [0, 1, 3, 6, 9, 99, 100, 123, 135, 147, 159]  # ~15 cols

# Ak užívateľ chce harmonické
if args.include_harmonics:
    harmonic_cols = range(186, 774)  # 2nd-50th harmonics
    df_harmonics = load_data(filepath, use_cols=harmonic_cols)
    # Spracuj osobitne
```

### 5.2 Pandas Thousands Separator

**Problém:**
```python
# Nesprávne
pd.read_csv(..., decimal=',')  # Pandas si myslí že ',' je thousands!
# "83616,805" → 83.6 ❌

# Správne
pd.read_csv(..., decimal=',', thousands='')  # Žiadny thousands separator
# "83616,805" → 83616.805 ✅
```

**Overenie:**
```python
# Test na prvých riadkoch
df_test = pd.read_csv(..., nrows=5)
assert df_test['P_total'].iloc[0] > 1000, "P_total is too small! Check thousands separator"
```

### 5.3 Fuzzy Matching - Ambiguity

**Problém:** Viac kandidátov pre jeden parameter

**Riešenie:**
```python
# Preferuj:
# 1. "priem" > "avg" > "min" > "max"
# 2. Kratší názov (menej slov)
# 3. Nižší index (skôr v súbore)

candidates.sort(key=lambda x: (
    -x[0],  # Score (higher = better)
    len(x[2].split()),  # Word count (lower = better)
    x[1]  # Index (lower = better)
))
```

### 5.4 Mixed Sampling Rate

**Problém:** Nekonzistentné Δt (napr. 60s, potom 120s)

**Riešenie:**
```python
if mixed_sampling:
    logger.warning(f"Mixed sampling detected! Top intervals: {dt_hist}")
    # Použij dominantný interval pre energy calc
    # Ale flag v reporte
```

---

## 🎯 6. Implementačné priority

### Priority 1: MVP (Minimum Viable Product)

**Cieľ:** Fungovať pre 90% use cases

```python
✅ Preprocess (fix ,/- values)
✅ Fuzzy match (P/S/PF/U/F total)
✅ Load core columns only
✅ Energy calculation
✅ Basic validation (ΣP vs P_total)
✅ XLSX export (summary + timeseries)
✅ PNG plots (power + PF)
```

**Čas: 2-3 dni**

### Priority 2: Extended Features

```python
✅ Per-phase power (P/S/Q L1N/L2N/L3N)
✅ Voltage imbalance
✅ All validation metrics
✅ Data quality report
✅ Acceptance criteria thresholds
✅ Detailed logging
```

**Čas: +2 dni**

### Priority 3: Advanced

```python
✅ THD analysis
✅ Harmonics (optional flag)
✅ Event detection (sags/swells)
✅ Chunked processing for 10M+ rows
✅ Progress bar
✅ Config file support
```

**Čas: +3 dni**

---

## 💡 7. Odporúčania

### 7.1 Kód štruktúra

```
fluke_processor/
├── __init__.py
├── main.py                 # CLI entry point
├── config.py               # Configuration
├── preprocessor.py         # Data cleaning
├── column_mapper.py        # Fuzzy matching
├── data_loader.py          # Pandas loading
├── calculator.py           # Energy & validations
├── validator.py            # Cross-checks
├── exporter.py             # XLSX & PNG generation
├── logger.py               # Logging setup
└── utils.py                # Helper functions

tests/
├── test_preprocessor.py
├── test_column_mapper.py
├── test_calculator.py
└── fixtures/
    └── sample_fluke.txt    # Small test file

docs/
└── USER_GUIDE.md

examples/
└── example_usage.py
```

### 7.2 CLI Interface

```bash
# Basic usage
python -m fluke_processor input.txt

# With options
python -m fluke_processor input.txt \
    --output-dir ./results \
    --include-harmonics \
    --chunk-size 50000 \
    --verbose

# Config file
python -m fluke_processor input.txt --config config.yaml
```

### 7.3 Testing Strategy

```python
# Test files
1. small.txt        (100 rows)    - unit tests
2. medium.txt       (10k rows)    - integration tests
3. large.txt        (1M rows)     - performance tests
4. corrupted.txt    (bad format)  - robustness tests
5. mixed_lang.txt   (SK/CZ/EN)    - fuzzy match tests
```

---

## 📈 8. Performance Estimates

### 8.1 Processing Time

| Riadkov | Stĺpce | Approach | Time | RAM |
|---------|--------|----------|------|-----|
| 1k | Core (~20) | Single | <1s | 10 MB |
| 10k | Core | Single | <3s | 50 MB |
| 100k | Core | Single | 15s | 200 MB |
| 1M | Core | Chunked | 90s | 300 MB |
| 10M | Core | Chunked | 15min | 500 MB |
| 1M | All (2413) | Chunked | 5min | 20 GB ❌ |

### 8.2 Bottlenecks

```
1. Preprocessing (regex):  20% času
2. Pandas loading:         40% času
3. Calculations:           30% času
4. XLSX export:            10% času
```

**Optimalizácie:**
- Použiť `pyarrow` engine namiesto `python` (2× rýchlejší)
- Vectorized operations (NumPy)
- Multiprocessing pre chunky (ak potrebné)

---

## ✅ 9. Záver a Next Steps

### Odporúčaný prístup:

**1. Hybrid Architecture** (Adaptive)
   - Auto-detect file size
   - Single-pass pre <100k riadkov
   - Chunked pre >100k riadkov

**2. Modular Design**
   - Každý modul testovateľný samostatne
   - Jasné API medzi modulmi
   - Konfigurovateľné cez CLI/config

**3. Implementation Phases**
   - Week 1: MVP (core functionality)
   - Week 2: Extended features
   - Week 3: Advanced + optimization

### Chceš, aby som:

A) **Vytvoril prototyp** (funkčný kód s MVP features)?
B) **Pokračoval v analýze** (hlbšie testy, edge cases)?
C) **Pripravil test data** (vytvorenie syntetických súborov)?
D) **Niečo iné**?

---

**Autor:** Claude Code Analysis
**Dátum:** 2025-11-12
**Verzia:** 1.0
