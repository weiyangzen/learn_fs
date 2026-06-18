# File Research: sources/os/linux/linux/fs/xfs/xfs_drain.h

Declares the deferred intent drain interface and documents why it exists.

Key contents:
- Under `CONFIG_XFS_DRAIN_INTENTS`, `struct xfs_defer_drain` stores an atomic pending count and waitqueue.
- Declares drain initialization, cleanup, waiter gate toggles, group intent get/put, drain, and busy checks.
- The large design comment explains scrub/repair collision risks with deferred metadata intent chains across transaction rolls and why per-group intent counting prevents false corruption findings or unsafe repair.
- Without drain-intent support, the drain struct is empty and group intent operations fall back to ordinary group get/put.

This header is mostly a concurrency contract for deferred work, scrub, and realtime/AG group metadata updates.
