<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config.json

## Purpose
Flat listing benchmark config for bucket `list-benchmark-tests`.

## Important APIs, Types, And Functions
JSON/configuration document rather than executable code.

## Control Flow
Declares twelve top-level test folders from 1,000 through 1,000,000 one-kilobyte files and no nested subdirectories.

## State And Persistence Behavior
No state by itself; the benchmark creates bucket/local structures described here.

## Dependencies
Depends on the listing benchmark `Directory` schema.

## Integration Points
Consumed by `listing_benchmark.py` through the `Directory` protobuf schema.

## Risks And Edge Cases
Large counts make setup expensive; 1M case is skipped unless `--run_1m_test` is set.

## Test Signals
Exercised indirectly by listing benchmark parsing and directory-creation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config.json -->
