# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_drain.c

## Purpose
Implements a passive drain counter for deferred metadata intents, used by scrub/repair to wait until active intent chains for an allocation group or realtime group have finished.

## Main APIs
- `xfs_defer_drain_wait_enable` and `xfs_defer_drain_wait_disable` toggle a static branch for waiter wakeup checks.
- `xfs_defer_drain_init` and `xfs_defer_drain_free` initialize and validate a drain.
- `xfs_group_intent_get` takes a group reference and increments its intent drain count.
- `xfs_group_intent_put` decrements the count and releases the group.
- `xfs_group_intent_drain` waits killably for the count to reach zero.
- `xfs_group_intent_busy` checks whether intents are pending.

## Key Behavior
The static key avoids waitqueue overhead when no drain waiters exist. Releasing the final intent wakes waiters only when the static branch is enabled and the waitqueue is active. A memory barrier pairs with waiter state setting before checking the waitqueue.

## Invariants
Callers waiting for a drain must not hold locks that prevent intent completion. Intent users hold a passive group reference for the lifetime of the declared update.
