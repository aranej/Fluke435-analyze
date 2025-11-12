"""
Calculator module for energy calculations and validations

Implements all power quality metrics, energy integration,
and cross-validation checks according to specification.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, List
from .config import THRESHOLDS

logger = logging.getLogger(__name__)


class Calculator:
    """
    Calculate energy, power quality metrics, and validations
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize calculator with dataframe

        Args:
            df: DataFrame with power quality data (must have datum and cas columns)
        """

        self.df = df.copy()
        self.results = {}

    def create_timestamp(self, date_col: str = 'datum', time_col: str = 'cas'):
        """
        Create timestamp column from separate date and time columns

        Args:
            date_col: Name of date column
            time_col: Name of time column
        """

        # Try multiple date formats
        date_formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']

        for fmt in date_formats:
            try:
                self.df['timestamp'] = pd.to_datetime(
                    self.df[date_col] + ' ' + self.df[time_col],
                    format=fmt + ' %H:%M:%S.%f',
                    dayfirst=True
                )
                break
            except:
                continue

        # Remove rows with invalid timestamps
        initial_count = len(self.df)
        self.df = self.df[self.df['timestamp'].notna()]
        removed = initial_count - len(self.df)

        if removed > 0:
            logger.warning(f"Removed {removed} rows with invalid timestamps")

        # Sort by timestamp
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)

        logger.info(f"Created timestamp column, {len(self.df):,} valid rows")

    def analyze_sampling(self) -> Dict:
        """
        Analyze sampling interval (Δt)

        Returns:
            Dict with dt_mode, dt_histogram, mixed_sampling flag
        """

        # Calculate Δt
        self.df['dt'] = self.df['timestamp'].diff().dt.total_seconds()

        # Get histogram
        dt_counts = self.df['dt'].value_counts().head(10)

        # Dominant Δt (mode)
        dt_mode = dt_counts.index[0] if len(dt_counts) > 0 else 60.0

        # Check for mixed sampling
        dominant_ratio = dt_counts.iloc[0] / len(self.df) if len(dt_counts) > 0 else 1.0
        mixed_sampling = dominant_ratio < THRESHOLDS['mixed_sampling_threshold']

        # Top 3 intervals
        dt_histogram = {}
        for i, (dt_val, count) in enumerate(dt_counts.head(3).items()):
            dt_histogram[f"interval_{i+1}_s"] = dt_val
            dt_histogram[f"interval_{i+1}_count"] = count
            dt_histogram[f"interval_{i+1}_percent"] = count / len(self.df) * 100

        result = {
            'dt_mode_s': dt_mode,
            'dt_mode_min': dt_mode / 60,
            'mixed_sampling': mixed_sampling,
            'dominant_ratio': dominant_ratio,
            **dt_histogram
        }

        self.results['sampling'] = result

        if mixed_sampling:
            logger.warning(f"Mixed sampling detected! Dominant interval: {dominant_ratio:.1%}")
        else:
            logger.info(f"Stable sampling: {dt_mode}s ({dt_mode/60:.2f} min)")

        return result

    def calculate_energy(self, power_col: str = 'P_total') -> Dict:
        """
        Calculate energy from power timeseries

        Args:
            power_col: Name of power column (in Watts)

        Returns:
            Dict with energy calculations
        """

        if 'dt' not in self.df.columns:
            raise ValueError("Must call analyze_sampling() first")

        if power_col not in self.df.columns:
            raise ValueError(f"Power column '{power_col}' not found")

        # Get dominant Δt
        dt_mode = self.results['sampling']['dt_mode_s']
        dt_h = dt_mode / 3600  # Convert to hours

        # Calculate energy in kWh
        E_kWh = self.df[power_col].sum() * dt_h / 1000

        result = {
            'power_column': power_col,
            'E_kWh': E_kWh,
            'P_mean_W': self.df[power_col].mean(),
            'P_min_W': self.df[power_col].min(),
            'P_max_W': self.df[power_col].max(),
            'dt_h': dt_h
        }

        logger.info(f"Energy ({power_col}): {E_kWh:.2f} kWh")

        return result

    def validate_power_balance(self,
                              total_col: str,
                              phase_cols: List[str]) -> Dict:
        """
        Validate sum of phases vs total

        Args:
            total_col: Name of total power column
            phase_cols: List of phase power column names

        Returns:
            Dict with validation metrics
        """

        # Check columns exist
        missing = [col for col in [total_col] + phase_cols if col not in self.df.columns]
        if missing:
            logger.warning(f"Columns not found: {missing}")
            return {'available': False}

        # Sum of phases
        phase_sum = self.df[phase_cols].sum(axis=1)

        # Relative error (with protection against zero)
        rel_err = np.abs(phase_sum - self.df[total_col]) / (np.abs(self.df[total_col]) + 1e-6)

        result = {
            'available': True,
            'total_col': total_col,
            'phase_cols': phase_cols,
            'rel_err_mean': rel_err.mean(),
            'rel_err_p50': rel_err.quantile(0.50),
            'rel_err_p95': rel_err.quantile(0.95),
            'rel_err_max': rel_err.max()
        }

        logger.info(f"Power balance ({total_col}): mean={rel_err.mean():.3f}, p95={rel_err.quantile(0.95):.3f}")

        return result

    def calculate_pf(self,
                    P_col: str = 'P_total',
                    S_col: str = 'S_total',
                    PF_measured_col: Optional[str] = 'PF_total') -> Dict:
        """
        Calculate PF and compare with measured values

        Args:
            P_col: Active power column
            S_col: Apparent power column
            PF_measured_col: Measured PF column (if available)

        Returns:
            Dict with PF metrics
        """

        # Calculate PF
        self.df['PF_calc'] = np.clip(
            self.df[P_col] / (self.df[S_col] + 1e-6),
            -1, 1
        )

        result = {
            'PF_calc_mean': self.df['PF_calc'].mean(),
            'PF_calc_min': self.df['PF_calc'].min(),
            'PF_calc_max': self.df['PF_calc'].max()
        }

        # Compare with measured if available
        if PF_measured_col and PF_measured_col in self.df.columns:
            diff = np.abs(self.df[PF_measured_col] - self.df['PF_calc'])

            result.update({
                'PF_measured_mean': self.df[PF_measured_col].mean(),
                'PF_diff_mean': diff.mean(),
                'PF_diff_p50': diff.quantile(0.50),
                'PF_diff_p95': diff.quantile(0.95),
                'PF_diff_max': diff.max()
            })

            logger.info(f"PF difference: mean={diff.mean():.4f}, p95={diff.quantile(0.95):.4f}")

        return result

    def validate_vector_power(self,
                             P_col: str = 'P_total',
                             Q_col: str = 'Q_total',
                             S_col: str = 'S_total') -> Dict:
        """
        Validate S² = P² + Q²

        Args:
            P_col: Active power
            Q_col: Reactive power
            S_col: Apparent power

        Returns:
            Dict with validation metrics
        """

        if Q_col not in self.df.columns:
            logger.warning(f"Column '{Q_col}' not found, skipping vector validation")
            return {'available': False}

        # Calculate S from P and Q
        S_calc = np.sqrt(self.df[P_col]**2 + self.df[Q_col]**2)

        # Relative error (only where S > 1 VA)
        mask = self.df[S_col] > 1
        rel_err = np.abs(self.df[S_col][mask] - S_calc[mask]) / self.df[S_col][mask]

        result = {
            'available': True,
            'samples_used': mask.sum(),
            'rel_err_mean': rel_err.mean(),
            'rel_err_p50': rel_err.quantile(0.50),
            'rel_err_p95': rel_err.quantile(0.95),
            'rel_err_max': rel_err.max()
        }

        logger.info(f"Vector validation (S²=P²+Q²): mean={rel_err.mean():.3f}, p95={rel_err.quantile(0.95):.3f}")

        return result

    def analyze_frequency(self, F_col: str = 'F') -> Dict:
        """
        Analyze frequency statistics

        Args:
            F_col: Frequency column name

        Returns:
            Dict with frequency stats
        """

        if F_col not in self.df.columns:
            return {'available': False}

        result = {
            'available': True,
            'F_mean_Hz': self.df[F_col].mean(),
            'F_min_Hz': self.df[F_col].min(),
            'F_max_Hz': self.df[F_col].max(),
            'F_std_Hz': self.df[F_col].std()
        }

        logger.info(f"Frequency: {result['F_mean_Hz']:.3f} Hz (±{result['F_std_Hz']:.3f})")

        return result

    def analyze_voltage_imbalance(self,
                                  voltage_cols: List[str] = ['U_L1N', 'U_L2N', 'U_L3N']) -> Dict:
        """
        Calculate voltage imbalance

        Imbalance = max(|U_i - U_avg|) / U_avg * 100 [%]

        Args:
            voltage_cols: List of voltage column names

        Returns:
            Dict with imbalance metrics
        """

        missing = [col for col in voltage_cols if col not in self.df.columns]
        if missing:
            logger.warning(f"Voltage columns not found: {missing}")
            return {'available': False}

        # Calculate average voltage
        U_avg = self.df[voltage_cols].mean(axis=1)

        # Calculate imbalance
        imbalances = []
        for col in voltage_cols:
            imb = np.abs(self.df[col] - U_avg) / U_avg * 100
            imbalances.append(imb)

        # Maximum imbalance per sample
        max_imbalance = pd.concat(imbalances, axis=1).max(axis=1)

        result = {
            'available': True,
            'imbalance_mean_percent': max_imbalance.mean(),
            'imbalance_p50_percent': max_imbalance.quantile(0.50),
            'imbalance_p95_percent': max_imbalance.quantile(0.95),
            'imbalance_max_percent': max_imbalance.max()
        }

        logger.info(f"Voltage imbalance: mean={result['imbalance_mean_percent']:.2f}%, "
                   f"p95={result['imbalance_p95_percent']:.2f}%")

        return result

    def get_summary(self) -> Dict:
        """
        Generate comprehensive summary of all calculations

        Returns:
            Dict with all results combined
        """

        summary = {
            'measurement_start': self.df['timestamp'].min(),
            'measurement_end': self.df['timestamp'].max(),
            'duration_hours': (self.df['timestamp'].max() - self.df['timestamp'].min()).total_seconds() / 3600,
            'total_samples': len(self.df),
            **self.results
        }

        return summary

    def check_acceptance_criteria(self) -> Dict[str, str]:
        """
        Check all acceptance criteria against thresholds

        Returns:
            Dict of {metric_name: 'PASS' | 'INFO' | 'ALERT'}
        """

        status = {}

        # Delta E
        if 'energy_comparison' in self.results:
            delta_E = self.results['energy_comparison'].get('delta_E_percent', 0)
            if delta_E <= THRESHOLDS['delta_E_percent']['pass']:
                status['delta_E'] = 'PASS'
            elif delta_E <= THRESHOLDS['delta_E_percent']['info']:
                status['delta_E'] = 'INFO'
            else:
                status['delta_E'] = 'ALERT'

        # PF difference
        if 'pf' in self.results:
            pf_diff = self.results['pf'].get('PF_diff_p95', 0)
            if pf_diff <= THRESHOLDS['PF_diff_p95']['pass']:
                status['PF_diff'] = 'PASS'
            elif pf_diff <= THRESHOLDS['PF_diff_p95']['info']:
                status['PF_diff'] = 'INFO'
            else:
                status['PF_diff'] = 'ALERT'

        # Overall status
        if all(s == 'PASS' for s in status.values()):
            status['overall'] = 'PASS'
        elif any(s == 'ALERT' for s in status.values()):
            status['overall'] = 'ALERT'
        else:
            status['overall'] = 'INFO'

        return status
