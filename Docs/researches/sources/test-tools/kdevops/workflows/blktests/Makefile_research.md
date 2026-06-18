# sources/test-tools/kdevops/workflows/blktests/Makefile

## Purpose
Converts blktests Kconfig values into Ansible variables and exposes targets for setup, baseline/dev runs, result collection, oscheck-only execution, and monitoring collection.

## Important APIs, Types, and Functions
Key variables are `BLKTESTS_ARGS`, `BLKTESTS_DYNAMIC_RUNTIME_VARS`, `WORKFLOW_ARGS`, and `EXTRA_VAR_INPUTS`. Targets include `extend-extra-args-blktests`, `blktests`, `blktests-baseline`, `blktests-dev`, result targets, skip/update variants, `monitor-results`, and help.

## Control Flow
Quote-stripped Kconfig values are assembled into `BLKTESTS_ARGS` and appended to `WORKFLOW_ARGS`. Runtime variables add rerun-failures or skip-run behavior. Targets call `ansible-playbook` with host limits, tags, skip-tags, and extra vars.

## State and Persistence Behavior
`extend-extra-args-blktests` appends `blktests_test_devs` to `$(KDEVOPS_EXTRA_VARS)`. Other state is produced by Ansible runs and copied results.

## Dependencies and Integration Points
Integrates with `playbooks/blktests.yml`, `playbooks/monitor-results.yml`, `extra_vars.yaml`, host groups, and runtime knobs such as `RUN_FAILURES` and `SKIP_RUN`.

## Risks and Edge Cases
Runtime extra-vars are hand-built and quote-sensitive. Repeated appends to `KDEVOPS_EXTRA_VARS` can duplicate keys unless regenerated elsewhere. Targets assume baseline/dev inventory groups where used.

## Test Signals
Use `make -n` for every target under different runtime knobs. Verify generated extra vars and run a minimal blktests baseline/result collection path.
