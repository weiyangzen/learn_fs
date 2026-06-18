# sources/test-tools/kdevops/scripts/test-linux-ab.sh

## Purpose
Runs a TAP-style local validation of all Linux A/B defconfig build methods without requiring full infrastructure bringup.

## Important APIs
`tap_result(result, test_name, details)` emits TAP lines and tracks counters. `check_condition(condition, test_name, error_msg)` evaluates shell conditions. `restore_state()` restores a `.config.backup.$$` at exit.

## Control flow
The script backs up `.config`, declares a TAP plan of `1..18`, loops over `target`, `9p`, and `builder`, runs `make mrproper`, applies `make defconfig-linux-ab-testing-$method`, generates `extra_vars.yaml`, checks A/B Kconfig symbols, and validates method-specific symbols. It then extracts baseline/dev refs and verifies they differ before printing a summary.

## State and persistence
It modifies `.config` and `extra_vars.yaml` via Make, with a trap restoring `.config` only. It leaves generated files from Make unless cleanup is handled elsewhere.

## Dependencies and integration
Requires `make`, kdevops defconfig targets, grep, awk, and shell arrays. Designed for CI containers where full bringup is not possible.

## Risks and test signals
The hard-coded TAP plan says 18, but the script emits additional ref extraction tests, so TAP consumers may see a plan mismatch. `eval` in `check_condition` is acceptable for fixed internal strings but should not receive user input. Success exits 0 with all checks passing.
