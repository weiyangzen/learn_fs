<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Kconfig -->
# sources/test-tools/kdevops/workflows/selftests/Kconfig

## Purpose
This Kconfig file configures Linux kernel selftests coverage for kdevops. It controls whether specific selftest subsystems are selected manually or as a vetted default set.

## Important Symbols
`SELFTESTS_KMOD_TIMEOUT_SET_BY_CLI` detects `KMOD_TIMEOUT` from the command line. Build helper flags include `SELFTESTS_BUILD_RADIX_TREE` and `SELFTESTS_BUILD_SELFTESTS_DIR`. `SELFTESTS_MANUAL_COVERAGE` defaults to `y` and exposes manual selections. Manual options include `SELFTESTS_TEST_BUNDLE_RADIX_TREE`, `SELFTESTS_SECTION_FIRMWARE`, `KMOD`, `MODULE`, `MAPLE`, `SYSCTL`, `XARRAY`, and `VMA`. When manual coverage is disabled, several sections default to enabled. `SELFTESTS_SECTION_KMOD_TIMEOUT` configures the kmod timeout and can be set from CLI.

## Control Flow and Integration
Selections use `select` to enable required build paths. The Makefile includes per-section test Makefiles and shows specific help only when manual coverage is enabled. Values marked `output yaml` feed Ansible variables for `playbooks/selftests.yml`.

## State, Persistence, and Dependencies
The generated configuration persists selected coverage and timeout values. It depends on kdevops Kconfig helpers such as `scripts/check-cli-set-var.sh` and `scripts/append-makefile-vars-int.sh`.

## Risks and Test Signals
Some help strings contain typos, but the symbol graph is clear. Defaults differ significantly between manual and automatic modes, so result comparisons should include the config. The kmod timeout is runner-specific and may need tuning. Test signals are generated YAML and successful selftests targets.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/selftests/Kconfig -->
