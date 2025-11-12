# Ukážkové výstupy analýzy Fluke 435

Tento adresár obsahuje príklady výstupných súborov vygenerovaných procesorom.

## Súbory

### 1. `fluke_analysis_example.xlsx` (138 KB)
Excel report obsahujúci 5 sheetov:
- **summary** - Základné štatistiky (energia, výkon, frekvencia, nesymetria)
- **validation** - Výsledky validácií (bilancie výkonov, vektorová validácia)
- **timeseries_power** - Kompletný časový rad všetkých meraných veličín
- **data_quality** - Informácie o vzorkovaní a kvalite dát
- **mapping_log** - Zoznam namapovaných stĺpcov

### 2. `timeseries_power.png` (198 KB)
Graf časového priebehu:
- Modrá krivka: Činný výkon P (kW)
- Červená krivka: Zdanlivý výkon S (kVA)

### 3. `timeseries_pf.png` (107 KB)
Graf Power Factor:
- Modrá plná čiara: Meraný PF
- Červená bodkovaná: Vypočítaný PF (P/S)

## Pôvod dát

Výstupy boli vygenerované z reálneho merania:
- **Súbor**: `2025-10-25_BD16.txt` (17.4 MB)
- **Prístroj**: Fluke 435 Series II
- **Obdobie**: 21.10.2025 16:01 - 22.10.2025 16:00 (24 hodín)
- **Vzorkovanie**: 60 sekúnd
- **Počet vzoriek**: 1,440

## Výsledky

- ✅ **Energia**: 1,691.71 kWh
- ✅ **ΔE**: 0.01% (PASS)
- ✅ **PF rozdiel**: 1.5% p95 (PASS)
- ✅ **Nesymetria napätia**: 0.78% p95 (PASS)
- ✅ **Celkový status**: PASS

## Ako vygenerovať vlastné výstupy

```bash
python3 process_fluke.py tvoj_subor.txt --verbose
```

Výstupy sa uložia do adresára `results/`.
