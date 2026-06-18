<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/requirements.in

## Purpose
Single-thread microbenchmark dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Includes pandas, BigQuery and Storage clients, pyarrow, pandas_gbq, google-crc32c, psutil, and setuptools.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Includes pandas, BigQuery and Storage clients, pyarrow, pandas_gbq, google-crc32c, psutil, and setuptools.

## Integration Points
Installed in a venv by `run_microbenchmark.sh` before read/write benchmark scripts run.

## Risks And Edge Cases
Heavy analytics dependencies can make setup slow; helper.py also relies on BigQuery auth.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/requirements.in -->
