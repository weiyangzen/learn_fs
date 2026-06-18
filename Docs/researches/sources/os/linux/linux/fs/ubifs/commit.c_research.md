# File Research: sources/os/linux/linux/fs/ubifs/commit.c

Purpose: UBIFS commit orchestration: transitions journal/index/LPT/orphan state from mutable journal updates into committed on-flash metadata while minimizing latency.

Key APIs:
- `ubifs_bg_thread`
- `ubifs_commit_required`
- `ubifs_request_bg_commit`
- `ubifs_run_commit`
- `ubifs_gc_should_commit`
- Debug helpers: `dbg_old_index_check_init`, `dbg_check_old_index`

Implementation notes:
- Commit is split into commit start under write-locked `commit_sem` and commit end after releasing it, allowing foreground filesystem work during bulk I/O.
- `nothing_to_commit()` avoids unnecessary flash writes when TNC and LPT are clean, except during mount/recovery/remount cases.
- `do_commit()` syncs journal heads, starts GC/log/TNC/LPT/orphan commit phases, captures lprops stats, ends TNC/LPT/orphan commit, checks old index, updates master node fields, completes log/GC/LPT post-commit, and returns state to resting.
- Background thread syncs write buffers and runs background commit when requested.
- Commit state machine includes resting, background, required, running-background, running-required, and broken states.

Concurrency and correctness:
- `cs_lock` protects commit state and wakeups.
- `commit_sem` serializes commit start with journal/TNC/LPT mutation.
- Failed commit marks `COMMIT_BROKEN`, wakes waiters, logs error, and switches UBIFS to read-only error mode.
- `ubifs_run_commit()` upgrades background-running commit to required and waits when another commit is already active.
- Debug old-index checking walks the previous index tree to verify recovery invariants: root level/sqnum, child ordering, key ranges, and old index preservation.
