# sources/test-tools/syzkaller/syz-cluster/overlays/local/test/kustomization.yaml

## Purpose
Kustomize overlay for automated local smoke testing.

## Important APIs, types, and functions
Includes `../common` and `../../common`, and generates `global-config` from the minimal test `global-config.yaml`.

## Control flow
The smoke script applies this rendered overlay after local infra and migrations, then waits for core deployments.

## State and persistence behavior
Uses local emulator and fake storage state from `../common`.

## Dependencies and integration points
Primary overlay consumed by `make k8s-config-test` in `local_cluster_test.sh`.

## Risks and edge cases
Minimal config means smoke coverage focuses on deployment/readiness/dashboard reachability, not full workflow/email functionality. Include order and generated config names must stay compatible with deployments.

## Test signals
High-value smoke signal through `local_cluster_test.sh`, which deploys this overlay and checks dashboard HTTP 200.
