# File Research: sources/os/linux/linux/block/blk-pm.c

Purpose: Implements request-based runtime power management support for block queues.

Key responsibilities:
- Initializes queue runtime PM state and enables autosuspend with an initial impossible delay.
- Pre-suspend path marks the queue `RPM_SUSPENDING`, sets PM-only mode, freezes the queue, switches usage ref to atomic mode, and permits suspend only if usage count is zero.
- On failed pre-suspend, restores `RPM_ACTIVE`, marks the device last busy, and clears PM-only mode.
- Post-suspend records `RPM_SUSPENDED` or returns to active on error.
- Pre-resume marks `RPM_RESUMING`.
- Post-resume marks active, records last busy, requests autosuspend, and clears PM-only if needed.

Concurrency and lifecycle notes:
- Uses `q->queue_lock` around `rpm_status` transitions.
- Uses queue freeze and `percpu_ref_switch_to_atomic_sync()` so later queue-enter callers observe PM-only state.
- Designed for request-based drivers, not bio-direct drivers.

Dependencies:
- Public runtime PM API and internal blk-mq freeze helpers.

Filesystem/block relevance:
- Prevents normal filesystem I/O from entering a queue while the underlying block device is runtime-suspended or suspending.
