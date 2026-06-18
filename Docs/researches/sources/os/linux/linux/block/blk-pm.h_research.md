# File Research: sources/os/linux/linux/block/blk-pm.h

Purpose: Internal inline helpers for blk runtime PM gating in queue entry and request completion paths.

Key contents:
- `blk_pm_resume_queue()` allows queue entry when no PM gating is active, allows PM requests during non-suspended states, otherwise requests device resume and denies entry.
- `blk_pm_mark_last_busy()` marks runtime PM last-busy for non-PM requests.
- Provides no-op stubs when `CONFIG_PM` is disabled.

Concurrency and lifecycle notes:
- Relies on queue PM-only state and `rpm_status` maintained by `blk-pm.c`.
- Separates PM requests (`RQF_PM`) from normal requests to avoid blocking resume-related I/O.

Dependencies:
- Runtime PM API.

Filesystem/block relevance:
- Small but important hook that keeps normal filesystem I/O from racing runtime suspend/resume.
