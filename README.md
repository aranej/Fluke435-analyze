# Fluke 435 - Analýza importu a exportu Power Log Classic 4.6

Tento repozitár obsahuje komplexnú dokumentáciu o procese importu dát z analyzátora kvality energie Fluke 435 do programu Power Log Classic 4.6 a následnom exporte do textového formátu.

## Obsah

### 📄 Dokumentácia

1. **[FLUKE_435_IMPORT_EXPORT_DOKUMENTACIA.md](FLUKE_435_IMPORT_EXPORT_DOKUMENTACIA.md)**
   - Kompletný návod na import dát z Fluke 435
   - Postup exportu z Power Log Classic 4.6
   - Workflow a riešenie problémov
   - Určené pre koncových používateľov

2. **[FORMAT_ANALYZA_TECHNICKA.md](FORMAT_ANALYZA_TECHNICKA.md)**
   - Detailná technická analýza formátu TSV súboru
   - Štruktúra 2413 stĺpcov dát
   - Príklady programatického spracovania (Python, Excel)
   - Určené pre vývojárov a analytikov

### 📊 Vzorové dáta

**[2025-10-25_BD16.txt](2025-10-25_BD16.txt)** (18 MB)
- Skutočný exportovaný súbor z Power Log Classic
- 24-hodinové meranie s minutovým intervalom
- 1440 záznamov × 2413 parametrov

## Rýchly prehľad

### Proces importu a exportu

```
┌─────────────┐
│  Fluke 435  │  Meranie kvality elektrickej energie
└──────┬──────┘
       │
       ├─→ Optický kábel OC4USB (RS232)
       └─→ SD karta (rýchlejšie)
       │
       ▼
┌──────────────────┐
│ Power Log Classic │  Analýza a spracovanie dát
│      4.6          │
└────────┬─────────┘
         │
         │ File | Export
         ▼
┌──────────────────┐
│  Textový súbor   │  TSV formát, 2413 stĺpcov
│  (.txt / .tsv)   │  Excel compatible
└──────────────────┘
```

### Formát exportovaného súboru

- **Formát:** TSV (Tab-Separated Values)
- **Kódovanie:** Windows-1250 (Central European)
- **Stĺpcov:** 2 413
- **Decimálny oddeľovač:** Čiarka (,)
- **Časový interval:** 1 minúta

### Kategórie meraných parametrov

| Kategória | Počet stĺpcov | Popis |
|-----------|---------------|-------|
| Časové údaje | 2 | Dátum, Čas |
| Napätie | 48 | L1N, L2N, L3N, NG - Min/Avg/Max |
| Prúd | 48 | L1, L2, L3, N - Min/Avg/Max |
| Frekvencia | 3 | Min, Priem, Max |
| Asymetria | 12 | Vn, Vz, An, Az |
| Výkon | 36 | W, VA, VAR - všetky fázy |
| Power Factor | 24 | PF, DPF |
| THD | 12 | Total Harmonic Distortion |
| Harmonické 2-50 | 1 588 | 49 harmonických × 4 fázy × 3 hodnoty |
| Fázové uhly | 200 | 50 harmonických × 4 fázy |
| Ostatné | 440 | Reserve/checksum |

## Použitie

### Pre používateľov

Prečítajte si [FLUKE_435_IMPORT_EXPORT_DOKUMENTACIA.md](FLUKE_435_IMPORT_EXPORT_DOKUMENTACIA.md) pre:
- Návod na pripojenie Fluke 435 k PC
- Postup importu dát do Power Log Classic
- Návod na export do textového súboru
- Riešenie bežných problémov

### Pre vývojárov

Prečítajte si [FORMAT_ANALYZA_TECHNICKA.md](FORMAT_ANALYZA_TECHNICKA.md) pre:
- Detailnú štruktúru formátu TSV
- Mapu všetkých 2413 stĺpcov
- Príklady kódu v Python a Excel
- Technické špecifikácie

## Rýchly štart - Python

```python
import pandas as pd

# Načítanie dát
df = pd.read_csv(
    '2025-10-25_BD16.txt',
    sep='\t',
    encoding='windows-1250',
    decimal=','
)

# Konverzia dátumu/času
df['Timestamp'] = pd.to_datetime(
    df['Dátum'] + ' ' + df['Čas'],
    format='%d.%m.%Y %H:%M:%S.%f'
)

# Prístup k dátam
voltage = df['Napätie L1N Priem']
current = df['Prúd L1 Priem']
power = df['Činný výkon Celkom Priem']

# Analýza
print(f"Priemerné napätie L1N: {voltage.mean():.2f} V")
print(f"Priemerný prúd L1: {current.mean():.2f} A")
print(f"Priemerný výkon: {power.mean():.2f} W")
```

## Rýchly štart - Excel

1. **Data → From Text/CSV**
2. **Nastavenia:**
   - File Origin: `1250 (Central European Windows)`
   - Delimiter: `Tab`
3. **Load data**
4. **Find & Replace:** `,` → `.` (pre anglické formátovanie)

## Požiadavky

### Hardvér
- Fluke 435 analyzátor
- PC s Windows Vista/7/8/10
- Optický kábel OC4USB alebo SD karta

### Softvér
- Power Log Classic 4.6 (alebo kompatibilná verzia)
- Microsoft Excel / Python / R (na analýzu dát)

## Kompatibilita

Power Log Classic podporuje:
- Fluke 345
- Fluke VR1710
- Fluke 1735
- Fluke 433/434/435

## Licencia

Dokumentácia je voľne dostupná pre vzdelávacie a komerčné účely.

## Príspevok

Našli ste chybu alebo máte návrh na zlepšenie? Vytvorte issue alebo pull request.

## Kontakt

Pre otázky a spätnú väzbu kontaktujte autora repozitára.

---

**Posledná aktualizácia:** 2025-11-12
**Verzia dokumentácie:** 1.0
