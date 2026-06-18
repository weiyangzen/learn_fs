# sources/test-tools/kdevops/workflows/demos/reboot-limit/Makefile

## Purpose
Implements and documents the reboot-limit workflow, converting Kconfig settings into Ansible variables and defining setup, run, loop, reset, and analysis targets.

## Important APIs, Types, and Functions
Important variables are `REBOOT_LIMIT_TEST_TYPE`, `REBOOT_LIMIT_ARGS`, `REBOOT_LIMIT_DATA*`, `REBOOT_LIMIT_MAX`, `REBOOT_LIMIT_LOOP`, `REBOOT_LIMIT_LOOP_KOTD`, and `WORKFLOW_ARGS`. Targets include baseline/dev runs, loop/kotd variants, resets, `reboot-limit-results`, and `reboot-limit-graph`.

## Control Flow
The Makefile builds workflow args, honors `COUNT` as max reboot override, and defines baseline/dev targets. Baseline/dev runs perform first-run/reset tasks followed by run/copy tasks. The dev target first checks for hosts in the `dev` group.

## State and Persistence Behavior
Ansible and scripts produce target counters, data under configured reboot-limit paths, copied results, and analysis/graph outputs.

## Dependencies and Integration Points
Integrates with `playbooks/reboot-limit.yml`, `extra_vars.yaml`, loop scripts, and `analyze_results.py`.

## Risks and Edge Cases
The dev-host grep only checks one line after `[dev]`, so comments/blank lines can cause false negatives. The setup target does not pass `extra_vars.yaml`, unlike run targets. Long loops need external monitoring.

## Test Signals
Dry-run all targets under compare mode, crash injection, and `COUNT=N`. Test no-dev and formatted-dev inventories. Run a `COUNT=1` smoke test.
