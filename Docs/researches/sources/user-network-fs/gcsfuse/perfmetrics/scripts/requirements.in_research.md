<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/requirements.in

## Purpose
Top-level perfmetrics script dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Pins Cloud Monitoring, grpc, protobuf, Google auth/API clients, requests, pytest, and test helper dependencies.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Pins Cloud Monitoring, grpc, protobuf, Google auth/API clients, requests, pytest, and test helper dependencies.

## Integration Points
Installed by generic load/VM metric wrappers before fetch/upload scripts run.

## Risks And Edge Cases
Version set is old in places and may conflict with subdirectory-specific protobuf pins if installed into the same user environment.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/requirements.in -->
