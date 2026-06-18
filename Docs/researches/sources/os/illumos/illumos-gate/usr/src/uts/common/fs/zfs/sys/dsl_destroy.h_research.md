# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_destroy.h

Read status: complete, 68 lines.

Purpose: dataset and snapshot destruction interfaces.

Key APIs:
- Snapshot destruction: `dsl_destroy_snapshots_nvl()`, `dsl_destroy_snapshot()`, check/sync implementations, and sync-task wrappers.
- Head dataset destruction: `dsl_destroy_head()`, `dsl_destroy_head_check_impl()`, `dsl_destroy_head_sync_impl()`, check/sync wrappers.
- `dsl_destroy_inconsistent()` handles inconsistent dataset destruction.
- Argument structs carry snapshot name/defer flag and head dataset name.

Dependencies: nvlist, DSL dataset, DMU transaction forward declarations.

Research notes:
- Exposes both public entry points and check/sync pieces for DSL synctask execution.
