# sources/test-tools/stress-ng/stress-lockf.c

Purpose: implements the `lockf` filesystem/OS stressor. It creates contention on byte-range advisory locks in a shared temporary file using `lockf()`, exercising blocking or nonblocking acquisition, unlock, and test paths.

Important APIs/types/functions: `stress_lockf_info_t` records a held lock offset; `stress_lockf_info_list_t` tracks active and reusable records. `stress_lockf_info_new()`, `stress_lockf_info_head_remove()`, and `stress_lockf_info_free()` maintain that list. `stress_lockf_unlock()` seeks to the oldest offset and unlocks it. `stress_lockf_contention()` repeatedly selects random offsets and calls `lockf(F_LOCK)` or `lockf(F_TLOCK)`.

Control flow: `stress_lockf()` creates a temp directory and a 64 KiB lock file, fills it with zeroed data, then forks a child pinned near the parent CPU. Parent and child both call the contention loop on the same file descriptor until the stressor stops. Held locks are capped at `LOCK_MAX`; when full, the oldest lock is released before acquiring another.

State and persistence: held lock metadata is per-process static list state with a free list for reuse. Temporary directory/file state is removed at shutdown. The child is killed and waited from the parent cleanup path.

Dependencies/integration: gated by `HAVE_LOCKF`. Uses stress-ng temp-file helpers, affinity helpers, fork retry/kill helpers, scheduler application, bogo counters, and `VERIFY_ALWAYS`.

Risks/test signals: `lockf` semantics vary over filesystems and are process-associated, so forked descriptor sharing matters. Unlock failure aborts to avoid retry loops on stale records. Useful signals are bogo progress, deterministic cleanup, capped lock list length, and unimplemented behavior when `lockf()` is unavailable.
