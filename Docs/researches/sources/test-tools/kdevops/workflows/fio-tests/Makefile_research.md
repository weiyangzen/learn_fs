# sources/test-tools/kdevops/workflows/fio-tests/Makefile

## Purpose
Provides make targets for running fio tests, baselines, result collection, graphing, comparison, trend analysis, multi-filesystem comparison, cleanup, and help.

## Important APIs, Types, and Functions
Targets are `fio-tests`, `fio-tests-baseline`, `fio-tests-results`, `fio-tests-graph`, `fio-tests-compare`, `fio-tests-trend-analysis`, `fio-tests-multi-fs-compare`, `fio-tests-clean-results`, and `fio-tests-help-menu`.

## Control Flow
Each action calls a dedicated playbook with `--extra-vars=@$(KDEVOPS_EXTRA_VARS)`. Cleanup removes `$(TOPDIR)/workflows/fio-tests/results/`. When enabled, cleanup is added to destroy dependencies.

## State and Persistence Behavior
The local results tree is persistent until `fio-tests-clean-results` removes it. Target state is managed by Ansible playbooks.

## Dependencies and Integration Points
Integrates with all fio-tests playbooks and `KDEVOPS_DESTROY_DEPS`.

## Risks and Edge Cases
Targets do not pass `LIMIT_HOSTS`. Cleanup uses direct `rm -rf`. There is no preflight for missing extra vars, playbooks, or graphing dependencies.

## Test Signals
Use `make -n` for every target, run cleanup on a disposable results tree, and smoke-test quick mode end to end.
