"""
Exporter module for generating XLSX reports and PNG plots

Creates comprehensive reports with multiple sheets and visualizations.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .config import PLOT_DPI, PLOT_FIGSIZE

logger = logging.getLogger(__name__)


class Exporter:
    """
    Export analysis results to XLSX and PNG
    """

    def __init__(self, output_dir: str = './results'):
        """
        Initialize exporter

        Args:
            output_dir: Directory for output files
        """

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Output directory: {self.output_dir}")

    def export_xlsx(self,
                   df: pd.DataFrame,
                   summary: Dict,
                   mapping_log: List[Dict],
                   filename: str = 'fluke_analysis.xlsx'):
        """
        Export comprehensive XLSX report with multiple sheets

        Args:
            df: Main dataframe with timeseries
            summary: Summary dict from Calculator
            mapping_log: Column mapping log
            filename: Output filename
        """

        filepath = self.output_dir / filename

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:

            # Sheet 1: Summary
            self._write_summary_sheet(writer, summary)

            # Sheet 2: Validation metrics
            self._write_validation_sheet(writer, summary)

            # Sheet 3: Timeseries (power)
            self._write_timeseries_sheet(writer, df)

            # Sheet 4: Data quality
            self._write_data_quality_sheet(writer, summary)

            # Sheet 5: Mapping log
            self._write_mapping_log_sheet(writer, mapping_log)

        logger.info(f"Exported XLSX: {filepath}")

    def _write_summary_sheet(self, writer, summary: Dict):
        """Write summary sheet with key metrics"""

        rows = []

        # Measurement info
        rows.append(['=== MEASUREMENT INFO ===', ''])
        rows.append(['Start Time', summary.get('measurement_start', 'N/A')])
        rows.append(['End Time', summary.get('measurement_end', 'N/A')])
        rows.append(['Duration (hours)', f"{summary.get('duration_hours', 0):.2f}"])
        rows.append(['Total Samples', f"{summary.get('total_samples', 0):,}"])
        rows.append(['', ''])

        # Sampling
        if 'sampling' in summary:
            s = summary['sampling']
            rows.append(['=== SAMPLING ===', ''])
            rows.append(['Dominant Interval (s)', f"{s.get('dt_mode_s', 0):.1f}"])
            rows.append(['Dominant Interval (min)', f"{s.get('dt_mode_min', 0):.2f}"])
            rows.append(['Mixed Sampling', 'YES' if s.get('mixed_sampling') else 'NO'])
            rows.append(['Dominant Ratio', f"{s.get('dominant_ratio', 0):.1%}"])
            rows.append(['', ''])

        # Energy
        if 'energy_total' in summary:
            e = summary['energy_total']
            rows.append(['=== ENERGY (TOTAL) ===', ''])
            rows.append(['Energy (kWh)', f"{e.get('E_kWh', 0):.2f}"])
            rows.append(['Power Mean (W)', f"{e.get('P_mean_W', 0):.1f}"])
            rows.append(['Power Min (W)', f"{e.get('P_min_W', 0):.1f}"])
            rows.append(['Power Max (W)', f"{e.get('P_max_W', 0):.1f}"])
            rows.append(['', ''])

        # Energy comparison
        if 'energy_comparison' in summary:
            ec = summary['energy_comparison']
            rows.append(['=== ENERGY COMPARISON ===', ''])
            rows.append(['E_total (kWh)', f"{ec.get('E_total_kWh', 0):.2f}"])
            rows.append(['E_phase_sum (kWh)', f"{ec.get('E_phase_sum_kWh', 0):.2f}"])
            rows.append(['Delta E (%)', f"{ec.get('delta_E_percent', 0):.2f}"])
            rows.append(['Status', ec.get('status', 'N/A')])
            rows.append(['', ''])

        # Power Factor
        if 'pf' in summary:
            pf = summary['pf']
            rows.append(['=== POWER FACTOR ===', ''])
            rows.append(['PF Calculated Mean', f"{pf.get('PF_calc_mean', 0):.3f}"])
            rows.append(['PF Measured Mean', f"{pf.get('PF_measured_mean', 0):.3f}"])
            rows.append(['|ΔPF| Mean', f"{pf.get('PF_diff_mean', 0):.4f}"])
            rows.append(['|ΔPF| P95', f"{pf.get('PF_diff_p95', 0):.4f}"])
            rows.append(['', ''])

        # Frequency
        if 'frequency' in summary:
            f = summary['frequency']
            if f.get('available'):
                rows.append(['=== FREQUENCY ===', ''])
                rows.append(['Mean (Hz)', f"{f.get('F_mean_Hz', 0):.3f}"])
                rows.append(['Min (Hz)', f"{f.get('F_min_Hz', 0):.3f}"])
                rows.append(['Max (Hz)', f"{f.get('F_max_Hz', 0):.3f}"])
                rows.append(['Std Dev (Hz)', f"{f.get('F_std_Hz', 0):.4f}"])
                rows.append(['', ''])

        # Voltage imbalance
        if 'voltage_imbalance' in summary:
            vi = summary['voltage_imbalance']
            if vi.get('available'):
                rows.append(['=== VOLTAGE IMBALANCE ===', ''])
                rows.append(['Mean (%)', f"{vi.get('imbalance_mean_percent', 0):.2f}"])
                rows.append(['P95 (%)', f"{vi.get('imbalance_p95_percent', 0):.2f}"])
                rows.append(['Max (%)', f"{vi.get('imbalance_max_percent', 0):.2f}"])
                rows.append(['', ''])

        # Acceptance criteria
        if 'acceptance' in summary:
            rows.append(['=== ACCEPTANCE CRITERIA ===', ''])
            for key, status in summary['acceptance'].items():
                rows.append([key, status])

        df_summary = pd.DataFrame(rows, columns=['Metric', 'Value'])
        df_summary.to_excel(writer, sheet_name='summary', index=False)

    def _write_validation_sheet(self, writer, summary: Dict):
        """Write validation metrics sheet"""

        rows = []

        # Power balance validations
        if 'power_balance_P' in summary:
            pb = summary['power_balance_P']
            if pb.get('available'):
                rows.append(['P: Sum of Phases vs Total', ''])
                rows.append(['  Mean Rel Error', f"{pb.get('rel_err_mean', 0):.4f}"])
                rows.append(['  P95 Rel Error', f"{pb.get('rel_err_p95', 0):.4f}"])
                rows.append(['  Max Rel Error', f"{pb.get('rel_err_max', 0):.4f}"])
                rows.append(['', ''])

        if 'power_balance_S' in summary:
            pb = summary['power_balance_S']
            if pb.get('available'):
                rows.append(['S: Sum of Phases vs Total', ''])
                rows.append(['  Mean Rel Error', f"{pb.get('rel_err_mean', 0):.4f}"])
                rows.append(['  P95 Rel Error', f"{pb.get('rel_err_p95', 0):.4f}"])
                rows.append(['', ''])

        # Vector validation
        if 'vector_validation' in summary:
            vv = summary['vector_validation']
            if vv.get('available'):
                rows.append(['Vector Validation (S² = P² + Q²)', ''])
                rows.append(['  Samples Used', f"{vv.get('samples_used', 0):,}"])
                rows.append(['  Mean Rel Error', f"{vv.get('rel_err_mean', 0):.4f}"])
                rows.append(['  P95 Rel Error', f"{vv.get('rel_err_p95', 0):.4f}"])
                rows.append(['', ''])

        df_validation = pd.DataFrame(rows, columns=['Validation', 'Value'])
        df_validation.to_excel(writer, sheet_name='validation', index=False)

    def _write_timeseries_sheet(self, writer, df: pd.DataFrame):
        """Write timeseries data sheet"""

        # Select relevant columns for export
        export_cols = ['timestamp']

        # Add available power columns
        power_cols = ['P_total', 'S_total', 'Q_total', 'PF_total', 'PF_calc',
                     'P_L1N', 'P_L2N', 'P_L3N',
                     'S_L1N', 'S_L2N', 'S_L3N',
                     'Q_L1N', 'Q_L2N', 'Q_L3N']

        voltage_cols = ['U_L1N', 'U_L2N', 'U_L3N']
        other_cols = ['F']

        for col in power_cols + voltage_cols + other_cols:
            if col in df.columns:
                export_cols.append(col)

        df_export = df[export_cols].copy()

        # Limit rows if too many (Excel has limits)
        if len(df_export) > 1_000_000:
            logger.warning(f"Timeseries has {len(df_export):,} rows, truncating to 1M for Excel")
            df_export = df_export.iloc[:1_000_000]

        df_export.to_excel(writer, sheet_name='timeseries_power', index=False)

    def _write_data_quality_sheet(self, writer, summary: Dict):
        """Write data quality metrics sheet"""

        rows = []

        if 'sampling' in summary:
            s = summary['sampling']

            # Top 3 intervals
            for i in range(1, 4):
                interval_key = f"interval_{i}_s"
                count_key = f"interval_{i}_count"
                percent_key = f"interval_{i}_percent"

                if interval_key in s:
                    rows.append([
                        f"Interval {i}",
                        f"{s[interval_key]:.1f}",
                        f"{s.get(count_key, 0):,}",
                        f"{s.get(percent_key, 0):.2f}"
                    ])

        df_quality = pd.DataFrame(rows,
                                 columns=['Rank', 'Interval (s)', 'Count', 'Percent'])
        df_quality.to_excel(writer, sheet_name='data_quality', index=False)

    def _write_mapping_log_sheet(self, writer, mapping_log: List[Dict]):
        """Write column mapping log sheet"""

        df_mapping = pd.DataFrame(mapping_log)
        df_mapping.to_excel(writer, sheet_name='mapping_log', index=False)

    def plot_power_timeseries(self,
                             df: pd.DataFrame,
                             filename: str = 'timeseries_power.png'):
        """
        Plot power timeseries (P and S)

        Args:
            df: DataFrame with timestamp, P_total, S_total
            filename: Output filename
        """

        filepath = self.output_dir / filename

        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)

        # Plot P and S
        if 'P_total' in df.columns:
            ax.plot(df['timestamp'], df['P_total'] / 1000,
                   label='P (kW)', linewidth=1, color='blue')

        if 'S_total' in df.columns:
            ax.plot(df['timestamp'], df['S_total'] / 1000,
                   label='S (kVA)', linewidth=1, alpha=0.7, color='red')

        ax.set_xlabel('Time')
        ax.set_ylabel('Power [kW / kVA]')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(filepath, dpi=PLOT_DPI)
        plt.close()

        logger.info(f"Exported plot: {filepath}")

    def plot_pf_comparison(self,
                          df: pd.DataFrame,
                          filename: str = 'timeseries_pf.png'):
        """
        Plot power factor comparison (measured vs calculated)

        Args:
            df: DataFrame with timestamp, PF_total, PF_calc
            filename: Output filename
        """

        filepath = self.output_dir / filename

        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)

        # Plot measured and calculated PF
        if 'PF_total' in df.columns:
            ax.plot(df['timestamp'], df['PF_total'],
                   label='PF measured', linewidth=1, color='blue')

        if 'PF_calc' in df.columns:
            ax.plot(df['timestamp'], df['PF_calc'],
                   label='PF calculated', linewidth=1,
                   linestyle='--', alpha=0.7, color='red')

        ax.set_xlabel('Time')
        ax.set_ylabel('Power Factor')
        ax.set_ylim([0, 1.05])
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(filepath, dpi=PLOT_DPI)
        plt.close()

        logger.info(f"Exported plot: {filepath}")
