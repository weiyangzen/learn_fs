# sources/test-tools/syzkaller/syz-cluster/overlays/local/test/global-config.yaml

## Purpose
Minimal local test global configuration used by the smoke test overlay.

## Important APIs, types, and functions
Sets `URL: http://localhost` and `parallelWorkflows: 1`.

## Control flow
Smoke deployment uses this small config to start core components without broad production/staging workload definitions.

## State and persistence behavior
No state. It limits runtime behavior by omitting email/tree/fuzz configuration.

## Dependencies and integration points
Used by local test overlay configMapGenerator.

## Risks and edge cases
Because it is minimal, it may not exercise config paths for email reporting, tree fetching, or fuzz targets.

## Test signals
Directly used by `local_cluster_test.sh`.
