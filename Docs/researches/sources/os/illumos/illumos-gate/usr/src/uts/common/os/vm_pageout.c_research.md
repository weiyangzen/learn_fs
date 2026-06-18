# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_pageout.c

Implements the kernel pageout daemon, page scanner scheduling, memory-pressure thresholds, async dirty-page push queue, and deadman detection for pageout stalls.

Key responsibilities:
- Defines and sizes free-memory thresholds: `lotsfree`, `desfree`, `minfree`, `throttlefree`, `pageout_reserve`, `needfree`, `deficit`, and scan rates.
- Calibrates page scanner spread and scan rate at boot through sampling.
- Runs one or more `pageout_scanner()` threads over disjoint regions of physical page memory.
- Uses a two-handed clock algorithm: the front hand clears reference state, and the back hand frees pages not referenced again.
- Queues dirty pages for asynchronous `VOP_PUTPAGE()` by the main `pageout()` thread.
- Signals memory waiters and integrates with kmem reaping, seg preaping, and kernel cage pressure.
- Panics through `pageout_deadman()` if pageout appears stuck too long in a single `VOP_PUTPAGE()` request.

Important paths:
- `setupclock()` computes memory thresholds, scan rates, scanner duty-cycle nanosecond budgets, hand spread, max page I/O, and desired page scanner count. It preserves boot-time tunable overrides in `clockinit`.
- `recalc_pagescanners()` chooses a scanner count from either `despagescanners` or memory size, bounded by `MAX_PSCAN_THREADS` and minimum per-scanner region size.
- `schedpaging()` runs four times per second, triggers kmem/seg reaping, computes `desscan` and `pageout_nsec` from memory pressure, adjusts scanner count, handles initial sampling, wakes scanners under low memory, and wakes waiters on `memavail_cv`.
- `pageout()` initializes the pageout process, async request pool, scanner thread, pageout scheduler, and kernel cage thread, then drains `push_list` by calling `VOP_PUTPAGE()` with `B_ASYNC | B_FREE`.
- `pageout_scanner()` waits on `proc_pageout->p_cv`, resets its memory-region clock hands when needed, scans up to `desscan` or its CPU budget, calls `checkpage()` for front and back hands, records samples, and exits excess scanner LWPs when scanner count shrinks.
- `checkpage()` skips kernel/free/locked/highly shared/locked-for-COW pages, uses `hat_pagesync()` to test/clear reference and modified state, demotes large pages when possible, queues dirty vnode pages for writeback, unloads clean pages, and disposes them with `VN_DISPOSE(B_FREE)`.
- `queue_io_request()` consumes a preallocated async request, holds the vnode from the caller, links it to `push_list`, and wakes the pusher when the request pool empties.

Locking and concurrency:
- `pageout_mutex` coordinates scanner wakeups, scanner count, and active scanner state.
- `push_lock` protects async request freelist, push queue, push counters, and condition variable.
- Page eligibility depends on page locks, HAT reference/modify bits, vnode holds, and page structure flags.
- Scanner threads can continue freeing clean pages while the pusher thread is blocked in filesystem writeback.

Filesystem relevance:
- Highly relevant to filesystem behavior. Dirty vnode-backed pages are reclaimed through `VOP_PUTPAGE()`, clean pages are returned with `VN_DISPOSE()`, filesystem writeback latency can stall memory reclaim, and pageout pressure interacts with swapfs, ZFS, and other filesystems that supply backing pages.
