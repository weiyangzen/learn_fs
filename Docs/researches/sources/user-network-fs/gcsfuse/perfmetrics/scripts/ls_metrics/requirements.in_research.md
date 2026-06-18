<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/requirements.in

## Purpose
Listing benchmark dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Includes argparse/configparser/statistics, numpy, mock, and protobuf 5.29.* for tests and generated `directory_pb2` use.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Includes argparse/configparser/statistics, numpy, mock, and protobuf 5.29.* for tests and generated `directory_pb2` use.

## Integration Points
Compiled requirements are installed by `run_ls_benchmark.sh`.

## Risks And Edge Cases
The wrapper must set protobuf Python implementation for generated-code compatibility.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/requirements.in -->
