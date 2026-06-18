# sources/test-tools/kdevops/workflows/fstests/Kconfig

## Purpose
Defines fstests workflow configuration for target filesystem, watchdogs, result trimming, repositories, test-device strategy, sparse/NVMe devices, run selection, soak duration, and journald integration.

## Important APIs, Types, and Functions
Important symbols include `FSTESTS_XFS/BTRFS/EXT4/NFS/CIFS/TMPFS`, `FSTESTS_FSTYP`, `FSTESTS_TFB_COPY_ENABLE`, watchdog symbols, per-filesystem sourced Kconfigs, `FSTESTS_GIT`, `FSTESTS_DATA`, test-device strategy choices, sparse settings, device/mount variables, run/custom group controls, large-disk controls, soak duration choices, and `FSTESTS_ENABLE_JOURNAL`.

## Control Flow
Most settings are gated by `KDEVOPS_WORKFLOW_ENABLE_FSTESTS`. Filesystem choice selects helper booleans and sources per-fs Kconfig. Non-network/non-tmpfs modes expose device strategies. Sparse mode exposes backing storage and loop defaults. Soak duration supports CLI and preset/custom choices.

## State and Persistence Behavior
Choices persist in `.config` and YAML. Runtime state includes cloned fstests, generated configs, sparse files, loop/NVMe devices, copied results, watchdog logs, and optional journal entries.

## Dependencies and Integration Points
Integrates with per-filesystem Kconfig/Makefiles, provider storage symbols, mirror/default git URLs, Ansible roles, and upstream fstests variables.

## Risks and Edge Cases
`FSTESTS_TFB_COPY_LIMIT` is guarded by `FSTESTS_TFB_ENABLE`, while the visible option is `FSTESTS_TFB_COPY_ENABLE`, likely hiding the limit. Device defaults can be destructive. Sparse loop numbering may conflict locally. High soak values can add days/months.

## Test Signals
Validate every filesystem choice, sparse/NVMe strategies, ZNS, watchdogs, custom group CLI detection, and soak presets. Generate configs and run a minimal disposable-device test.
