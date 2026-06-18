# File Research: sources/os/linux/linux/fs/xfs/xfs_drain.c

Implements the deferred-intent drain mechanism used to let online scrub/repair wait for active deferred metadata updates in an allocation group or realtime group.

Key behavior:
- Uses a static branch `xfs_defer_drain_waiter_gate` so release-side waiter checks are cheap when nobody can wait.
- `xfs_defer_drain_init/free` initialize and assert zero pending count.
- Internal grab/release helpers increment/decrement the atomic count and wake waiters when it reaches zero.
- `xfs_group_intent_get` obtains a group reference and declares an intent against that group.
- `xfs_group_intent_put` releases the intent and the group reference.
- `xfs_group_intent_drain` waits killably until no intents remain.
- `xfs_group_intent_busy` reports whether any intent is active.

The comments explain the core invariant: deferred work must hold intent counts across transaction rolls so scrub does not observe transient cross-structure inconsistency.
