<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Makefile -->
# sources/test-tools/kdevops/workflows/selftests/Makefile

## Purpose
This Makefile wires the selftests workflow into kdevops targets, dynamic runtime variables, per-section helpers, and help output.

## Important Targets and Variables
`SELFTESTS_DYNAMIC_RUNTIME_VARS` starts with `"kdevops_run_selftests": True` and conditionally appends `selftests_skip_run` and `selftests_skip_reboot` based on `SKIP_RUN` and `SKIP_REBOOT`. It includes section Makefiles for firmware, module, kmod, maple, sysctl, and xarray. Targets are `selftests`, `selftests-baseline`, `selftests-results`, `selftests-check-results`, `selftests-help-main`, `selftests-help-menu`, and `selftests-help-menu-targets`.

## Control Flow
`selftests` runs `playbooks/selftests.yml` while skipping run/copy/check tags, so it prepares/builds. `selftests-baseline` limits to `baseline`, passes runtime vars, and runs vars, test execution, result copy, and result check tags. Result-only and check-only targets narrow tag sets.

## State, Persistence, and Dependencies
State flows through Ansible, inventory groups, generated YAML, copied test results, and per-section Makefile variables. It depends on `LIMIT_HOSTS`, `TOPDIR`, and included test Makefiles.

## Risks and Test Signals
Only some section Makefiles are included directly; a VMA section exists in Kconfig but is not visibly included here unless pulled indirectly elsewhere. Runtime variable construction is string-based JSON/YAML, so quoting errors can break Ansible. Test signals are successful Ansible runs and check_results output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Makefile -->
