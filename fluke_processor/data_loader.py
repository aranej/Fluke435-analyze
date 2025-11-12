"""
Data Loader module for reading Fluke 435 data files

Supports both single-pass and chunked processing modes.
Automatically selects optimal mode based on file size.
"""

import pandas as pd
import logging
from typing import Optional, List
from pathlib import Path
from .config import (PANDAS_SETTINGS, CHUNK_SIZE_DEFAULT,
                     FILE_SIZE_THRESHOLD_MB, ENCODING_OUTPUT)

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Load Fluke 435 data with appropriate strategy (single-pass vs chunked)
    """

    def __init__(self, filepath: str):
        """
        Initialize loader

        Args:
            filepath: Path to preprocessed (clean) data file
        """

        self.filepath = Path(filepath)

        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Estimate file characteristics
        self.file_size_mb = self.filepath.stat().st_size / 1024 / 1024

    def load_data(self,
                 use_cols: Optional[List[int]] = None,
                 chunk_size: Optional[int] = None,
                 auto_mode: bool = True,
                 verbose: bool = False) -> pd.DataFrame:
        """
        Load data with optimal strategy

        Args:
            use_cols: List of column indices to load (None = all)
            chunk_size: Chunk size for chunked reading (None = auto)
            auto_mode: Automatically choose single-pass vs chunked
            verbose: Print progress information

        Returns:
            DataFrame with loaded data
        """

        # Decide on strategy
        if auto_mode:
            use_chunked = self.file_size_mb > FILE_SIZE_THRESHOLD_MB
        else:
            use_chunked = chunk_size is not None

        if use_chunked:
            if chunk_size is None:
                chunk_size = CHUNK_SIZE_DEFAULT

            logger.info(f"Loading data (CHUNKED mode, chunk_size={chunk_size:,})")
            return self._load_chunked(use_cols, chunk_size, verbose)
        else:
            logger.info(f"Loading data (SINGLE-PASS mode)")
            return self._load_single_pass(use_cols)

    def _load_single_pass(self, use_cols: Optional[List[int]]) -> pd.DataFrame:
        """Load entire file in one pass"""

        df = pd.read_csv(
            self.filepath,
            encoding=ENCODING_OUTPUT,
            usecols=use_cols,
            **PANDAS_SETTINGS
        )

        logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
        logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")

        return df

    def _load_chunked(self,
                     use_cols: Optional[List[int]],
                     chunk_size: int,
                     verbose: bool) -> pd.DataFrame:
        """Load file in chunks and concatenate"""

        chunks = []
        total_rows = 0

        reader = pd.read_csv(
            self.filepath,
            encoding=ENCODING_OUTPUT,
            usecols=use_cols,
            chunksize=chunk_size,
            **PANDAS_SETTINGS
        )

        for i, chunk in enumerate(reader, 1):
            chunks.append(chunk)
            total_rows += len(chunk)

            if verbose and i % 10 == 0:
                logger.info(f"  Loaded chunk {i} ({total_rows:,} rows so far)")

        df = pd.concat(chunks, ignore_index=True)

        logger.info(f"Loaded {len(df):,} rows from {len(chunks)} chunks")
        logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")

        return df

    def load_with_mapping(self,
                         column_mapping: dict,
                         required: List[str] = None,
                         **kwargs) -> tuple[pd.DataFrame, dict]:
        """
        Load data using column mapping

        Args:
            column_mapping: Dict of {logical_name: column_index}
            required: List of required logical column names
            **kwargs: Additional arguments for load_data()

        Returns:
            Tuple of (DataFrame, reverse_mapping)
            reverse_mapping = {column_index: logical_name}
        """

        # Get indices to load
        indices = [idx for idx in column_mapping.values() if idx is not None]

        # Check required columns
        if required:
            missing = [name for name in required
                      if column_mapping.get(name) is None]
            if missing:
                raise ValueError(f"Required columns not found: {missing}")

        # Load data
        df = self.load_data(use_cols=indices, **kwargs)

        # Create reverse mapping for renaming
        reverse_mapping = {idx: name
                          for name, idx in column_mapping.items()
                          if idx is not None}

        # Rename columns
        # Pandas returns columns in order of use_cols, so we need to map by position
        idx_to_position = {idx: pos for pos, idx in enumerate(sorted(indices))}
        new_column_names = []

        for idx in sorted(indices):
            logical_name = reverse_mapping.get(idx, f"col_{idx}")
            new_column_names.append(logical_name)

        df.columns = new_column_names

        logger.info(f"Renamed {len(new_column_names)} columns to logical names")

        return df, reverse_mapping
