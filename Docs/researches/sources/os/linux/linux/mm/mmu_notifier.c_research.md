# File Research: sources/os/linux/linux/mm/mmu_notifier.c

MMU notifier core for secondary MMUs and interval subscribers. This file coordinates invalidation callbacks, notifier registration/lifetime, mm teardown release notifications, young-bit callbacks, and interval-tree collision detection for shadow page-table users.

Key responsibilities:
- Maintains `struct mmu_notifier_subscriptions` per mm, including classic hlist notifiers, interval-tree notifiers, invalidation sequence state, active invalidation counts, waitqueue, and deferred interval-tree updates.
- Implements `mmu_interval_read_begin()` and interval invalidation sequencing for sleeping shadow-PTE setup/teardown protocols.
- Implements release-time invalidation for both interval-tree subscribers and classic hlist subscribers.
- Implements young-bit operations: clear-and-flush young, clear young, and test young.
- Implements invalidate-range start/end dispatch for interval and hlist notifiers, including non-blocking `-EAGAIN` handling.
- Provides notifier registration APIs, single-notifier get/put APIs, unregister, async free via SRCU, and module exit synchronization.
- Provides interval notifier insertion/removal, both with and without caller-held mmap write lock.

Important behavior:
- Interval invalidation uses a sequence value where odd values mean a colliding invalidation is active; readers sleep if their observed sequence equals the active invalidating sequence.
- Multiple invalidation writers can be active concurrently; the interval tree is only mutable in the partially excluded state or via deferred add/remove lists drained at final invalidation end.
- `mn_itree_invalidate()` calls interval `invalidate_start`/`invalidate_finish` pairs or legacy `invalidate`, collecting finish callbacks in a lockless list.
- Classic hlist callbacks are protected by a global SRCU domain so unregister/release can wait for in-flight callbacks.
- Non-blocking invalidations that receive `-EAGAIN` call `invalidate_range_end` for already-started notifiers and warn if a blocking callback fails.
- `__mmu_notifier_register()` installs the subscription object under mmap write lock and `mm_take_all_locks()`, with release/acquire ordering for unlocked readers.
- `mmu_notifier_put()` removes the subscription from the list and frees asynchronously through `call_srcu()`.
- Interval insertion grabs an mm count pin and may defer tree insertion if invalidation is in progress; removal waits for any deferred invalidation sequence to finish.

Dependencies:
- SRCU, RCU hlist traversal, interval trees, spinlocks, wait queues, mm lifetime pins, mmap locks, `mm_take_all_locks()`, and notifier operation contracts used by KVM, HMM, GPUs, RDMA, and other secondary-MMU users.

Notable risks:
- Callback ordering is correctness-critical: drivers must drop shadow mappings before core MM frees or repurposes PTEs/pages.
- Interval-tree add/remove during invalidation cannot use sleeping locks and relies on deferred-list draining at final invalidation end.
- `mmu_notifier_put()` is asynchronous; modules using it must call `mmu_notifier_synchronize()` before unload.
- Non-blocking invalidation callbacks must return only expected retry errors and cannot also require normal end callbacks after failing start.
