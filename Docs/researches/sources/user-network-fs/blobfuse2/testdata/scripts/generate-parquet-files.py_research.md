<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py -->
# sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py

Source path: `sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py`

## Purpose
Generates random Parquet data files for testdata workloads.

## Important APIs, Types, And Functions
Functions: `random_row_count`. Classes: none declared. Imports: `pandas`, `numpy`, `random`.

## Control Flow
Uses pandas, NumPy, and random row counts to build data frames and write Parquet files.

## State And Persistence
Persists generated Parquet files in the current working directory or configured output path.

## Dependencies And Integration Points
Integrates with Python runtime packages, benchmark datasets, mounted filesystem paths, and JSON/Parquet/report artifacts used by blobfuse2 performance experiments.

## Risks
Requires pandas/pyarrow-compatible parquet support; output volume depends on random row counts.

## Test Signals
Signals are successful script exit, valid generated JSON/Parquet/report files, timing metrics, and absence of unexpected read/classification/data-generation exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/testdata/scripts/generate-parquet-files.py -->
