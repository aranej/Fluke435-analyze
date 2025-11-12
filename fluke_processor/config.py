"""
Configuration settings for Fluke 435 Data Processor
"""

# File processing settings
ENCODING_INPUT = 'cp1250'
ENCODING_OUTPUT = 'utf-8'
CHUNK_SIZE_DEFAULT = 20000
FILE_SIZE_THRESHOLD_MB = 100  # Switch to chunked processing above this

# Pandas settings
PANDAS_SETTINGS = {
    'sep': '\t',
    'decimal': ',',
    'thousands': '',  # CRITICAL: No thousands separator!
    'on_bad_lines': 'skip',
    'engine': 'python'
    # Note: low_memory not supported with python engine
}

# Column mapping - aggregation preference
AGG_PREFERENCE = ['priem', 'avg', 'mean', 'priemer']

# Column keywords for fuzzy matching
# Each entry is a list of keywords that ALL must be present (AND logic)
# For multi-language support, each language variant should be a separate entry
COLUMN_KEYWORDS = {
    'datum': ['datum'],  # Slovak/Czech
    'cas': ['cas'],      # Slovak/Czech

    # Power - Total
    'P_total': ['cinny', 'vykon', 'celkom'],
    'S_total': ['va', 'full', 'celkom'],
    'Q_total': ['var', 'celkom'],
    'PF_total': ['pf', 'celkom'],
    'DPF_total': ['dpf', 'celkom'],

    # Power - Per phase
    'P_L1N': ['cinny', 'vykon', 'l1n'],
    'P_L2N': ['cinny', 'vykon', 'l2n'],
    'P_L3N': ['cinny', 'vykon', 'l3n'],

    'S_L1N': ['va', 'full', 'l1n'],
    'S_L2N': ['va', 'full', 'l2n'],
    'S_L3N': ['va', 'full', 'l3n'],

    'Q_L1N': ['var', 'l1n'],
    'Q_L2N': ['var', 'l2n'],
    'Q_L3N': ['var', 'l3n'],

    # Voltage (require all keywords to match - singular form)
    'U_L1N': ['napatie', 'l1n'],
    'U_L2N': ['napatie', 'l2n'],
    'U_L3N': ['napatie', 'l3n'],

    # Frequency
    'F': ['frekvencia'],

    # THD
    'THD_V_L1N': ['thd', 'v', 'l1n'],
    'THD_V_L2N': ['thd', 'v', 'l2n'],
    'THD_V_L3N': ['thd', 'v', 'l3n'],

    'THD_A_L1': ['thd', 'a', 'l1'],
    'THD_A_L2': ['thd', 'a', 'l2'],
    'THD_A_L3': ['thd', 'a', 'l3'],
}

# Acceptance criteria thresholds
THRESHOLDS = {
    'delta_E_percent': {
        'pass': 1.0,    # ≤ 1%
        'info': 3.0,    # 1-3%
        'alert': 3.0    # > 3%
    },
    'PF_diff_p95': {
        'pass': 0.05,   # ≤ 0.05
        'info': 0.1,    # 0.05-0.1
        'alert': 0.1    # > 0.1
    },
    'S_vec_err_p95': {
        'pass': 0.3,    # ≤ 0.3
        'info': 0.6,    # 0.3-0.6
        'alert': 0.6    # > 0.6
    },
    'voltage_imbalance_p95': {
        'pass': 2.0,    # ≤ 2%
        'info': 3.0,    # 2-3%
        'alert': 3.0    # > 3%
    },
    'mixed_sampling_threshold': 0.95  # Dominant Δt must be ≥95%
}

# Output settings
OUTPUT_XLSX_SHEETS = [
    'summary',
    'validation',
    'timeseries_power',
    'data_quality',
    'mapping_log'
]

OUTPUT_PNG_PLOTS = [
    'timeseries_power.png',
    'timeseries_pf.png'
]

# Plot settings
PLOT_DPI = 150
PLOT_FIGSIZE = (12, 6)
