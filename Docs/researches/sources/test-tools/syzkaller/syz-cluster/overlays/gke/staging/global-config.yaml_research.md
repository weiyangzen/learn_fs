# sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/global-config.yaml

## Purpose
Staging GKE global configuration.

## Important APIs, types, and functions
Sets `URL: https://staging.ci.syzbot.org`, `parallelWorkflows: 2`, email reporting via dashapi with staging client/from/support/list values, one `torvalds` tree, and a simple default KASAN fuzz target.

## Control flow
Staging services consume this config to run a smaller syz-cluster environment with fewer workflows and reduced target scope.

## State and persistence behavior
No direct persistence; controls staging external integrations and workflow volume.

## Dependencies and integration points
Same config schema as production, consumed by app environment, controller, reporter, workflows, and email reporter.

## Risks and edge cases
Staging still uses external dashapi/lists and kernel repos, so incorrect recipients or context prefix can affect real systems. Reduced config may miss production-only bugs.

## Test signals
Useful as a lower-risk deployment target; no direct tests in this file.
