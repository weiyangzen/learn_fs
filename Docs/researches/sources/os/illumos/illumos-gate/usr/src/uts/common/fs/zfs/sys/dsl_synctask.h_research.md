# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_synctask.h

Read status: complete, 127 lines.

Purpose: DSL sync task framework definitions and space-check policy enum.

Key structures and APIs:
- Function typedefs define check, sync, and signal callbacks.
- `zfs_space_check_t` policies range from normal space checks through reserved/extra-reserved/destroy/channel-program checks to no-check/discard-checkpoint behavior.
- `dsl_sync_task_t` stores TXG list node, pool, TXG, expected space, space-check policy, check/sync funcs, arg, error, and no-waiter flag.
- APIs: `dsl_sync_task_sync()`, `dsl_sync_task()`, `dsl_sync_task_nowait()`, `dsl_early_sync_task()`, `dsl_early_sync_task_nowait()`, and `dsl_sync_task_sig()`.

Important implementation constraints:
- Space-check enum documents slop-space thresholds and why destructive operations may still need checks when checkpoints exist.
- Sync tasks separate preflight validation from syncing-context mutation.

Dependencies: TXG, ZFS context, DSL pool forward declaration, DMU transactions.

Research notes:
- This is the common framework behind many administrative DSL operations such as create, destroy, property set, and key changes.
