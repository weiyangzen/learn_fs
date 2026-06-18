# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/spa_checkpoint.h

This header declares pool checkpoint accounting and discard-thread entry points.

Core definitions:
- `spa_checkpoint_info_t` stores checkpoint timestamp and disk space consumed by checkpoint-preserved blocks.

Public API surface:
- User-facing operations: `spa_checkpoint()` and `spa_checkpoint_discard()`.
- Background discard zthr hooks: `spa_checkpoint_discard_thread_check()` and `spa_checkpoint_discard_thread()`.
- Stats export: `spa_checkpoint_get_stats()`.

Risk-sensitive invariants:
- Checkpoint space is pool-level accounting and must align with checkpointed uberblock semantics.
- Discard work is asynchronous through `zthr_t`; check/sync code must coordinate with pool lifecycle.
