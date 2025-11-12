"""
Column Mapper module for fuzzy matching of headers

Handles multi-language (SK/CZ/EN) column names with diacritics,
various spellings, and aggregation preferences.
"""

import re
import unicodedata
import logging
from typing import List, Optional, Dict
from .config import COLUMN_KEYWORDS, AGG_PREFERENCE, ENCODING_INPUT

logger = logging.getLogger(__name__)


class ColumnMapper:
    """
    Maps logical column names to physical column indices using fuzzy matching
    """

    def __init__(self, header_line: str = None, columns: List[str] = None):
        """
        Initialize mapper with either header line or column list

        Args:
            header_line: Tab-separated header line
            columns: List of column names
        """

        if columns is not None:
            self.columns = columns
        elif header_line is not None:
            self.columns = header_line.strip().split('\t')
        else:
            self.columns = []

        self.mapping = {}
        self.normalized_columns = [self._normalize(col) for col in self.columns]

    @staticmethod
    def _remove_diacritics(text: str) -> str:
        """Remove diacritics from text"""
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize column name for fuzzy matching

        Steps:
        1. Remove diacritics
        2. Lowercase
        3. Replace non-alphanumeric with space
        4. Collapse multiple spaces
        5. Unify phase notation (l1 n → l1n)
        """

        # Remove diacritics
        text = ColumnMapper._remove_diacritics(text)

        # Lowercase
        text = text.lower()

        # Non-alnum → space
        text = re.sub(r'[^a-z0-9]+', ' ', text)

        # Collapse spaces
        text = re.sub(r'\s+', ' ', text).strip()

        # Unify phase notation
        text = text.replace('l1 n', 'l1n')
        text = text.replace('l2 n', 'l2n')
        text = text.replace('l3 n', 'l3n')

        return text

    def find_column(self,
                   keywords: List[str],
                   prefer: List[str] = None,
                   require_all: bool = True) -> Optional[int]:
        """
        Find column index by keywords with fuzzy matching

        Args:
            keywords: List of keywords (all must match if require_all=True)
            prefer: Aggregation preference (e.g., ['priem', 'avg'])
            require_all: If True, all keywords must match

        Returns:
            Column index or None if not found
        """

        if prefer is None:
            prefer = AGG_PREFERENCE

        candidates = []

        for i, norm_col in enumerate(self.normalized_columns):

            # Check if keywords match
            if require_all:
                matches = all(kw in norm_col for kw in keywords)
            else:
                matches = any(kw in norm_col for kw in keywords)

            if not matches:
                continue

            # Score by aggregation preference
            score = 0
            for j, pref in enumerate(prefer):
                if pref in norm_col:
                    score = len(prefer) - j  # Higher score = better
                    break

            # Also consider word count (prefer shorter/more specific)
            word_count = len(norm_col.split())

            candidates.append((score, word_count, i, self.columns[i]))

        if not candidates:
            return None

        # Sort by: score (desc), word count (asc), index (asc)
        candidates.sort(key=lambda x: (-x[0], x[1], x[2]))

        return candidates[0][2]  # Return index

    def auto_map(self, column_specs: Dict[str, List[str]] = None) -> Dict[str, Optional[int]]:
        """
        Automatically map all common columns

        Args:
            column_specs: Dict of {logical_name: [keywords]}
                         If None, uses COLUMN_KEYWORDS from config

        Returns:
            Dict of {logical_name: column_index or None}
        """

        if column_specs is None:
            column_specs = COLUMN_KEYWORDS

        mapping = {}

        for logical_name, keywords in column_specs.items():
            idx = self.find_column(keywords)
            mapping[logical_name] = idx

            if idx is not None:
                logger.debug(f"Mapped '{logical_name}' → col {idx}: {self.columns[idx]}")
            else:
                logger.warning(f"Could not find column for '{logical_name}' (keywords: {keywords})")

        self.mapping = mapping
        return mapping

    def get_mapped_indices(self, required: List[str] = None) -> List[int]:
        """
        Get list of mapped column indices

        Args:
            required: List of required logical column names

        Returns:
            List of indices (excluding None values)

        Raises:
            ValueError if required columns are missing
        """

        indices = []

        for name, idx in self.mapping.items():
            if idx is not None:
                indices.append(idx)
            elif required and name in required:
                raise ValueError(f"Required column '{name}' not found in file")

        return sorted(set(indices))

    def get_mapping_log(self) -> List[Dict[str, any]]:
        """
        Get mapping log for export/debugging

        Returns:
            List of dicts with {target, source, index} for each mapping
        """

        log = []

        for logical_name, idx in sorted(self.mapping.items()):
            log.append({
                'target': logical_name,
                'source': self.columns[idx] if idx is not None else 'NOT FOUND',
                'index': idx if idx is not None else -1
            })

        return log

    @classmethod
    def from_file(cls, filepath: str, encoding: str = None):
        """
        Create mapper by reading header from file

        Args:
            filepath: Path to data file
            encoding: File encoding (None = auto-detect)

        Returns:
            ColumnMapper instance
        """

        if encoding is None:
            # Try UTF-8 first (clean files), then fallback to CP1250 (raw files)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    header = f.readline()
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding=ENCODING_INPUT, errors='replace') as f:
                    header = f.readline()
        else:
            with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                header = f.readline()

        return cls(header_line=header)
