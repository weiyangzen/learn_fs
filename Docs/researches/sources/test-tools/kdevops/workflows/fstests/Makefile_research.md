# sources/test-tools/kdevops/workflows/fstests/Makefile

## Purpose
Maps fstests Kconfig settings into Ansible variables, includes filesystem-specific fragments, and exposes setup, run, config, result, trim, monitoring, and display targets.

## Important APIs, Types, and Functions
Important variables are `FSTESTS_ARGS`, `FSTESTS_ARGS_SEPARATED`, `FSTESTS_ARGS_DIRECT`, `FSTESTS_BASELINE_EXTRA`, `FSTYP`, `FS_CONFIG`, `FSTESTS_DYNAMIC_RUNTIME_VARS`, `LAST_KERNEL`, `FIND_PATH`, `PATTERN`, and `XARGS_ARGS`. Targets cover setup, baseline/dev/tests, config/debug, TFB list/trim, results, monitoring, and `fstests-show-results`.

## Control Flow
The Makefile builds workflow args, conditionally includes per-filesystem/sparse fragments, and appends runtime flags for reruns, skips, journald, initial baseline, start-after, skip tests, and count. Targets call `playbooks/fstests.yml` with specific limits, tags, and extra vars.

## State and Persistence Behavior
Reads `workflows/fstests/results/last-kernel.txt` for display path selection. Runtime artifacts include generated configs, sparse backing devices, copied results, TFB-trimmed outputs, and journal forwarding.

## Dependencies and Integration Points
Integrates with per-filesystem Makefile fragments, `playbooks/fstests.yml`, `monitor-results.yml`, `extra_vars.yaml`, baseline/dev groups, and upstream xunit result files.

## Risks and Edge Cases
Hand-built extra-vars strings are quote-sensitive. `fstests-show-results` relies on `find | xargs` behavior for empty input. `COUNT` is delegated as `oscheck_extra_args`. Result display depends on coherent `last-kernel.txt`.

## Test Signals
Use `make -n` with runtime knobs, run `fstests-config-debug`, smoke-test sparse-device baseline, verify TFB list/trim, and check `fstests-show-results` on empty/populated results.
