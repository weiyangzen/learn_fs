# sources/test-tools/kdevops/workflows/blktests/Kconfig

## Purpose
Defines blktests workflow configuration: watchdog behavior, source repository locations, data/install paths, test devices, manual section coverage, and result-copy policy.

## Important APIs, Types, and Functions
Important symbols include `BLKTESTS_WATCHDOG*`, `BLKTESTS_GIT`, `BLKTESTS_DATA`, `BLKTRACE_GIT`, `NBD_GIT`, `NBD_VERSION`, `BLKTESTS_DATA_TARGET`, `BLKTESTS_TEST_DEVS`, `BLKTESTS_MANUAL_COVERAGE`, per-section `BLKTESTS_SECTION_*`, and `BLKTESTS_RESULTS_ALL`.

## Control Flow
Most configuration is gated by `KDEVOPS_WORKFLOW_ENABLE_BLKTESTS`. Watchdog suboptions appear only under `BLKTESTS_WATCHDOG`. Manual coverage exposes selectable test sections; automatic coverage supplies defaults. Mirror-aware defaults use shell helper checks.

## State and Persistence Behavior
Choices persist in `.config` and are consumed by Makefile/Ansible generation. Data path options control cloned repositories and installation paths on targets.

## Dependencies and Integration Points
Depends on kdevops provider, mirror, libvirt, guestfs, and kernel CI symbols. The blktests Makefile consumes these values for `WORKFLOW_ARGS`.

## Risks and Edge Cases
`BLKTESTS_DBENCH_GIT_URL` references `HAVE_MIRROR_XFSDUMP` in a mirror default, likely a copy/paste bug. Device defaults are topology-sensitive. Reset-on-hang is intentionally disruptive.

## Test Signals
Resolve Kconfig under mirror/non-mirror, each storage bus, manual/automatic coverage, and watchdog modes. Verify generated extra vars and actual target device existence.
