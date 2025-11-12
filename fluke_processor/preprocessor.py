"""
Preprocessor module for cleaning Fluke 435 data files

Handles:
- Encoding conversion (CP1250 → UTF-8)
- Missing zeros before comma (,123 → 0,123)
- Missing zeros after minus (-,123 → -0,123)
- Space-minus patterns ( \- → -)
- Empty values (tab-tab → tab-0,0-tab)
"""

import re
import logging
from pathlib import Path
from typing import Optional
from .config import ENCODING_INPUT, ENCODING_OUTPUT

logger = logging.getLogger(__name__)


def preprocess_line(line: str) -> str:
    """
    Apply all preprocessing fixes to a single line

    Args:
        line: Raw line from file

    Returns:
        Cleaned line with all fixes applied
    """

    # 1. Fix space-minus patterns
    line = line.replace(' \\- ', '-')
    line = line.replace('\\-', '-')

    # 2. Fix negative missing zero:  -,XXX  →  -0,XXX
    line = re.sub(r'(^|\t)-,', r'\g<1>-0,', line)

    # 3. Fix positive missing zero:  ,XXX  →  0,XXX
    line = re.sub(r'(^|\t),', r'\g<1>0,', line)

    # 4. Fix empty values:  \t\t  →  \t0,0\t
    # Apply multiple times to catch consecutive empties
    for _ in range(3):
        line = re.sub(r'\t\t', '\t0,0\t', line)

    return line


def preprocess_file(input_path: str,
                   output_path: Optional[str] = None,
                   verbose: bool = False) -> tuple[str, dict]:
    """
    Preprocess Fluke 435 data file

    Creates a clean UTF-8 copy with all formatting issues fixed.
    This is done as a separate step for traceability and audit.

    Args:
        input_path: Path to raw input file (CP1250 encoded)
        output_path: Path for clean output file (UTF-8). If None, appends '_clean.txt'
        verbose: Print progress information

    Returns:
        Tuple of (output_path, statistics_dict)

    Statistics dict contains:
        - input_file: Original file path
        - output_file: Clean file path
        - total_lines: Number of lines processed
        - lines_modified: Number of lines that were changed
        - encoding_errors: Number of encoding errors encountered
    """

    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_clean.txt"
    else:
        output_path = Path(output_path)

    stats = {
        'input_file': str(input_path),
        'output_file': str(output_path),
        'total_lines': 0,
        'lines_modified': 0,
        'encoding_errors': 0
    }

    logger.info(f"Preprocessing: {input_path} → {output_path}")

    try:
        with open(input_path, 'r', encoding=ENCODING_INPUT, errors='replace') as fin:
            with open(output_path, 'w', encoding=ENCODING_OUTPUT) as fout:

                for line_no, line in enumerate(fin, 1):
                    stats['total_lines'] += 1

                    # Check for encoding errors
                    if '�' in line:
                        stats['encoding_errors'] += 1

                    # Apply fixes
                    original_line = line
                    clean_line = preprocess_line(line)

                    if clean_line != original_line:
                        stats['lines_modified'] += 1

                    fout.write(clean_line)

                    # Progress reporting
                    if verbose and line_no % 10000 == 0:
                        logger.info(f"  Processed {line_no:,} lines...")

    except Exception as e:
        logger.error(f"Error preprocessing file: {e}")
        raise

    # Log summary
    logger.info(f"Preprocessing complete:")
    logger.info(f"  Total lines: {stats['total_lines']:,}")
    logger.info(f"  Lines modified: {stats['lines_modified']:,} "
                f"({stats['lines_modified']/stats['total_lines']*100:.1f}%)")
    logger.info(f"  Encoding errors: {stats['encoding_errors']:,}")
    logger.info(f"  Output: {output_path}")

    return str(output_path), stats


def estimate_file_info(filepath: str) -> dict:
    """
    Quick scan of file to estimate size and row count

    Args:
        filepath: Path to file

    Returns:
        Dict with file_size_mb, estimated_rows, estimated_cols
    """

    filepath = Path(filepath)

    file_size = filepath.stat().st_size
    file_size_mb = file_size / 1024 / 1024

    # Count lines (fast)
    with open(filepath, 'rb') as f:
        line_count = sum(1 for _ in f)

    # Get column count from header
    with open(filepath, 'r', encoding=ENCODING_INPUT, errors='replace') as f:
        header = f.readline()
        col_count = len(header.split('\t'))

    return {
        'file_size_mb': file_size_mb,
        'estimated_rows': line_count - 1,  # Exclude header
        'estimated_cols': col_count
    }
