# sources/test-tools/stress-ng/stress-rmap.c

Purpose: implements `rmap`, a reverse-mapping memory stressor that maps overlapping windows from one backing file into many virtual addresses and has multiple child processes write/verify strided ownership patterns through them.

Important APIs/types/functions: `stress_rmap_info` exposes `rmap-procs`. `stress_rmap_touch()` writes pointer-derived check values at strides based on child index and verifies them. `stress_rmap_child()` iterates mappings in forward, reverse, random, and partial orders, optionally calling `msync()`. A shared `counter_lock` coordinates bogo increments across children.

Control flow: `stress_rmap()` configures child count, installs SIGCHLD handling, creates shared PID state and a lock, creates an unlinked temp backing file sized for staggered mappings, fallocates it, maps 64 overlapping 16-page windows with padding pages between them, then forks children. Children wait for parent sync, install SIGALRM exit handling, then loop touching assigned stripes across each mapping. The parent waits until the shared bogo condition stops, then kills/waits children.

State and persistence: state consists of an unlinked temp file, shared file-backed mappings, anonymous padding mappings, shared PID state, and the counter lock. Cleanup unmaps all windows and paddings, closes the fd, removes the temp directory, destroys the lock, and unmaps PID state.

Dependencies and integration points: uses `core-killpid`, `core-out-of-memory`, `core-signal`, `core-pragma`, temp filesystem helpers, `shim_fallocate()`, sync start lists, lock helpers, scheduler settings, and OOM adjustment.

Risks and test signals: overlapping writable mappings and multi-process verification can expose kernel rmap, writeback, or cache coherency issues. Risks include fork limits, fallocate failure, and child failure propagation. Test signals are no check-value mismatches, successful child termination, and correct cleanup of all mappings.
