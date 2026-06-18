<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/requirements.in

## Purpose
Rename benchmark Python dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Includes argparse/statistics plus numpy and Google API/auth/monitoring packages for statistics, Sheets upload, and VM metrics.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Includes argparse/statistics plus numpy and Google API/auth/monitoring packages for statistics, Sheets upload, and VM metrics.

## Integration Points
Compiled to hashed `requirements.txt` consumed by `run_rename_benchmark.sh`.

## Risks And Edge Cases
Mixes stdlib module names (`argparse`, `statistics`) with third-party packages; pinned transitive versions are only in compiled output.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/requirements.in -->
