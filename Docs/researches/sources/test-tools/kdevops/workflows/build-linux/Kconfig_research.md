# sources/test-tools/kdevops/workflows/build-linux/Kconfig

## Purpose
Configures the build-linux workflow: result directory, repeat count, make jobs, target, cleaning/stat collection, optional dedicated build filesystem, tag selection, and multi-filesystem hooks.

## Important APIs, Types, and Functions
Important symbols include `BUILD_LINUX_RESULTS_DIR`, `BUILD_LINUX_REPEAT_COUNT`, `BUILD_LINUX_MAKE_JOBS`, `BUILD_LINUX_TARGET`, `BUILD_LINUX_CLEAN_BETWEEN`, `BUILD_LINUX_COLLECT_STATS`, `BUILD_LINUX_STORAGE_ENABLE`, `BUILD_LINUX_DEVICE`, `BUILD_LINUX_FSTYPE`, XFS block/sector sizes, `BUILD_LINUX_USE_LATEST_TAG`, `BUILD_LINUX_CUSTOM_TAG`, and `BUILD_LINUX_ALLOW_MODIFICATIONS`.

## Control Flow
Most settings are gated by `KDEVOPS_WORKFLOW_ENABLE_BUILD_LINUX`. Storage choices appear only when storage is enabled. XFS block/sector choices appear only under XFS. `Kconfig.multifs` is sourced only when storage is enabled and declared hosts are not used.

## State and Persistence Behavior
Options are stored in `.config` and YAML output. The results directory determines where logs, raw timing JSON, summary JSON, visualizations, and reports persist.

## Dependencies and Integration Points
Consumed by build-linux Makefile, Ansible roles, and scripts under `workflows/build-linux/scripts`. Depends on provider-specific storage symbols.

## Risks and Edge Cases
Large repeat counts and clean builds are expensive. Large XFS block/sector sizes require support. Device defaults may be destructive if topology assumptions are wrong.

## Test Signals
Validate storage disabled/enabled, each filesystem, XFS size constraints, latest/custom tag modes, generated extra vars, and a one-build smoke run.
