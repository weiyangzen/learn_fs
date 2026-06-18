# File Research: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.h

Public interface for Btrfs async workqueues.

Key points:
- Defines callback types:
  - `btrfs_func_t` for normal work.
  - `btrfs_ordered_func_t` for ordered completion/free callbacks.
- `struct btrfs_work` stores the callbacks, embedded `work_struct`, ordered list node, owning `btrfs_workqueue`, and flags.
- Warns consumers not to touch internal fields below the callbacks.
- Declares allocation for normal and ordered workqueues, work initialization/queueing, destruction, max active adjustment, owner queries, congestion query, and flushing.

Role in system:
- This is the small stable API used by Btrfs subsystems that need deferred work with optional ordered completion.
