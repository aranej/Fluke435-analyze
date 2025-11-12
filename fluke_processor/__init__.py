"""
Fluke 435 Data Processor

A robust tool for processing electrical power quality data exported from
Fluke 435 analyzers via Power Log Classic 4.6.

Features:
- Fuzzy column matching (SK/CZ/EN)
- Robust preprocessing (missing zeros, encoding issues)
- Energy calculations and cross-validations
- XLSX reports with multiple sheets
- PNG visualizations
- Chunked processing for large files (up to 10M rows)

Author: Claude Code Analysis
Version: 1.0.0
Date: 2025-11-12
"""

__version__ = "1.0.0"
__author__ = "Claude Code Analysis"

from .preprocessor import preprocess_file
from .column_mapper import ColumnMapper
from .data_loader import DataLoader
from .calculator import Calculator
from .exporter import Exporter

__all__ = [
    'preprocess_file',
    'ColumnMapper',
    'DataLoader',
    'Calculator',
    'Exporter'
]
