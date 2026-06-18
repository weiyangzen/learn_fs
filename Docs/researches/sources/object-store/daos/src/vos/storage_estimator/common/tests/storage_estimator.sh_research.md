# sources/object-store/daos/src/vos/storage_estimator/common/tests/storage_estimator.sh

## Purpose
Smoke and unit-test driver for the DAOS storage estimator CLI and Python model tests.

## Important APIs, Types, And Functions
Shell functions `print_header` and `check_retcode` provide readable sections and cleanup-on-exit. The script creates a temporary directory, sources `utils/sl/setup_local.sh`, runs pytest marker groups when pytest exists, and then exercises `daos_storage_estimator.py` commands.

## Control Flow
The script sets `set -e` and an EXIT trap. It runs unit/object-class pytest suites, then CLI help and smoke flows for `create_example`, `read_csv`, `read_yaml`, and `explore_fs`. It tests object classes SX, RP_3GX, EC_16P2GX, checksum mode, aggregation mode, IO-size overrides, EC cell/chunk overrides, and YAML round trips.

## State And Persistence
Writes all generated files under a temporary directory and removes it in the exit trap. It depends on the caller's DAOS project setup to provide CLI and library paths.

## Dependencies And Integration
Depends on bash, pytest, Python CLI `daos_storage_estimator.py`, sample CSV/test files, and `setup_local.sh`.

## Risks
If pytest is missing, unit tests are skipped but smoke tests still run. The trap passes `${BASH_COMMAND}` unquoted, so command strings with spaces are lossy in the status message. Environment setup is mandatory and failures abort early. The script mutates no repository files.

## Test Signals
Successful completion indicates importability, marker tests, command help, sample generation, CSV ingestion, YAML ingestion, filesystem exploration, checksum paths, and EC aggregation smoke coverage.
