#!/usr/bin/env python3
"""
Fluke 435 Data Processor - Main Script

Comprehensive analysis of Fluke 435 power quality data exported via Power Log Classic 4.6.

Usage:
    python process_fluke.py input.txt [options]

Example:
    python process_fluke.py 2025-10-25_BD16.txt --output-dir ./results --verbose

Author: Claude Code Analysis
Version: 1.0.0
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

from fluke_processor import (
    preprocess_file,
    ColumnMapper,
    DataLoader,
    Calculator,
    Exporter
)
from fluke_processor.preprocessor import estimate_file_info


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""

    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    """Main processing pipeline"""

    parser = argparse.ArgumentParser(
        description='Process Fluke 435 power quality data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python process_fluke.py data.txt

  # With custom output directory
  python process_fluke.py data.txt --output-dir ./my_results

  # Verbose output
  python process_fluke.py data.txt --verbose

  # Skip preprocessing (if already clean)
  python process_fluke.py data_clean.txt --skip-preprocess

For more information, see README.md
        """
    )

    parser.add_argument('input_file',
                       help='Path to Fluke 435 data file (TSV format)')

    parser.add_argument('--output-dir', '-o',
                       default='./results',
                       help='Output directory for results (default: ./results)')

    parser.add_argument('--skip-preprocess',
                       action='store_true',
                       help='Skip preprocessing step (use if file is already clean)')

    parser.add_argument('--chunk-size',
                       type=int,
                       default=None,
                       help='Chunk size for reading large files (default: auto)')

    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output')

    parser.add_argument('--version',
                       action='version',
                       version='Fluke Processor 1.0.0')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Fluke 435 Data Processor v1.0.0")
    logger.info("=" * 80)

    # Check input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # Estimate file info
    logger.info("\n--- FILE INFO ---")
    file_info = estimate_file_info(str(input_path))
    logger.info(f"File size: {file_info['file_size_mb']:.1f} MB")
    logger.info(f"Estimated rows: {file_info['estimated_rows']:,}")
    logger.info(f"Estimated columns: {file_info['estimated_cols']:,}")

    # STEP 1: Preprocessing
    logger.info("\n--- STEP 1: PREPROCESSING ---")

    if args.skip_preprocess:
        logger.info("Skipping preprocessing (using input file as-is)")
        clean_file = str(input_path)
    else:
        clean_file, preprocess_stats = preprocess_file(
            str(input_path),
            verbose=args.verbose
        )
        logger.info(f"Created clean file: {clean_file}")

    # STEP 2: Column Mapping
    logger.info("\n--- STEP 2: COLUMN MAPPING ---")

    mapper = ColumnMapper.from_file(clean_file)
    column_mapping = mapper.auto_map()

    # Check critical columns
    critical_cols = ['datum', 'cas', 'P_total', 'S_total']
    missing_critical = [col for col in critical_cols if column_mapping.get(col) is None]

    if missing_critical:
        logger.error(f"Critical columns not found: {missing_critical}")
        logger.error("Cannot proceed without these columns.")
        sys.exit(1)

    logger.info(f"Successfully mapped {sum(1 for v in column_mapping.values() if v is not None)} columns")

    # STEP 3: Load Data
    logger.info("\n--- STEP 3: LOADING DATA ---")

    loader = DataLoader(clean_file)
    df, reverse_mapping = loader.load_with_mapping(
        column_mapping,
        required=['datum', 'cas', 'P_total', 'S_total'],
        chunk_size=args.chunk_size,
        verbose=args.verbose
    )

    logger.info(f"Loaded {len(df):,} rows × {len(df.columns)} columns")

    # STEP 4: Calculations
    logger.info("\n--- STEP 4: CALCULATIONS ---")

    calc = Calculator(df)

    # Create timestamp
    calc.create_timestamp(date_col='datum', time_col='cas')

    # Analyze sampling
    sampling_result = calc.analyze_sampling()

    # Calculate energies
    energy_total = calc.calculate_energy('P_total')
    calc.results['energy_total'] = energy_total

    # Energy comparison (if phases available)
    if all(col in df.columns for col in ['P_L1N', 'P_L2N', 'P_L3N']):
        energy_phases = []
        for phase in ['P_L1N', 'P_L2N', 'P_L3N']:
            e = calc.calculate_energy(phase)
            energy_phases.append(e['E_kWh'])

        E_phase_sum = sum(energy_phases)
        E_total = energy_total['E_kWh']
        delta_E_percent = abs(E_phase_sum - E_total) / E_total * 100

        calc.results['energy_comparison'] = {
            'E_total_kWh': E_total,
            'E_phase_sum_kWh': E_phase_sum,
            'delta_E_percent': delta_E_percent,
            'status': 'PASS' if delta_E_percent <= 1.0 else ('INFO' if delta_E_percent <= 3.0 else 'ALERT')
        }

        logger.info(f"Energy comparison: ΔE = {delta_E_percent:.2f}% "
                   f"[{calc.results['energy_comparison']['status']}]")

    # Power Factor
    if 'PF_total' in df.columns:
        pf_result = calc.calculate_pf('P_total', 'S_total', 'PF_total')
        calc.results['pf'] = pf_result

    # Validations
    if all(col in df.columns for col in ['P_L1N', 'P_L2N', 'P_L3N']):
        pb_P = calc.validate_power_balance('P_total', ['P_L1N', 'P_L2N', 'P_L3N'])
        calc.results['power_balance_P'] = pb_P

    if all(col in df.columns for col in ['S_L1N', 'S_L2N', 'S_L3N']):
        pb_S = calc.validate_power_balance('S_total', ['S_L1N', 'S_L2N', 'S_L3N'])
        calc.results['power_balance_S'] = pb_S

    # Vector validation
    if 'Q_total' in df.columns:
        vv = calc.validate_vector_power('P_total', 'Q_total', 'S_total')
        calc.results['vector_validation'] = vv

    # Frequency
    if 'F' in df.columns:
        freq_result = calc.analyze_frequency('F')
        calc.results['frequency'] = freq_result

    # Voltage imbalance
    if all(col in df.columns for col in ['U_L1N', 'U_L2N', 'U_L3N']):
        vi_result = calc.analyze_voltage_imbalance(['U_L1N', 'U_L2N', 'U_L3N'])
        calc.results['voltage_imbalance'] = vi_result

    # Check acceptance criteria
    acceptance = calc.check_acceptance_criteria()
    calc.results['acceptance'] = acceptance

    logger.info(f"\nOverall Status: {acceptance.get('overall', 'N/A')}")

    # STEP 5: Export
    logger.info("\n--- STEP 5: EXPORTING RESULTS ---")

    exporter = Exporter(output_dir=args.output_dir)

    # Get summary
    summary = calc.get_summary()

    # Get mapping log
    mapping_log = mapper.get_mapping_log()

    # Export XLSX
    xlsx_filename = f"fluke_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    exporter.export_xlsx(calc.df, summary, mapping_log, filename=xlsx_filename)

    # Export plots
    if 'P_total' in calc.df.columns and 'S_total' in calc.df.columns:
        exporter.plot_power_timeseries(calc.df)

    if 'PF_total' in calc.df.columns and 'PF_calc' in calc.df.columns:
        exporter.plot_pf_comparison(calc.df)

    # DONE
    logger.info("\n" + "=" * 80)
    logger.info("PROCESSING COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Results saved to: {args.output_dir}/")
    logger.info(f"  - XLSX report: {xlsx_filename}")
    logger.info(f"  - PNG plots: timeseries_power.png, timeseries_pf.png")

    if args.skip_preprocess:
        logger.info(f"  - Clean file: (skipped)")
    else:
        logger.info(f"  - Clean file: {clean_file}")

    logger.info(f"\nOverall Status: {acceptance.get('overall', 'N/A')}")

    # Exit code based on status
    if acceptance.get('overall') == 'ALERT':
        sys.exit(2)  # Alert condition
    elif acceptance.get('overall') == 'INFO':
        sys.exit(1)  # Info condition
    else:
        sys.exit(0)  # Pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
