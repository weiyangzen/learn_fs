<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/requirements.in

## Purpose
GKE example workload dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Contains absl, Google Cloud Storage/API, Monitoring, and BigQuery clients needed by fio/dlio Helm generators and parsers.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Contains absl, Google Cloud Storage/API, Monitoring, and BigQuery clients needed by fio/dlio Helm generators and parsers.

## Integration Points
Installed in a local venv by `run-gke-tests.sh`.

## Risks And Edge Cases
Unpinned input depends on compiled hash output for reproducibility.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/requirements.in -->
