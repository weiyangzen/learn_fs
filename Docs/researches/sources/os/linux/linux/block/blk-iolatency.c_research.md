# File Research: sources/os/linux/linux/block/blk-iolatency.c

## Summary
Implements the cgroup `io.latency` controller, an rq-qos policy that protects configured latency targets by throttling peer cgroups through queue-depth limits and induced delay.

## Main Responsibilities
- Track per-cgroup I/O latency over rolling windows.
- Walk the blkcg hierarchy on bio submission and completion.
- Limit in-flight bios through `rq_wait` queue-depth throttling.
- Scale sibling cgroup queue depths up or down based on protected group latency.
- Apply blkcg induced delay when queue depth is already at one and root-issued work is still causing pressure.
- Expose the cgroup `io.latency` file.

## Key APIs and Hooks
- rq-qos hooks: `blkcg_iolatency_throttle()`, `blkcg_iolatency_done_bio()`, `blkcg_iolatency_exit()`.
- Initialization: `blk_iolatency_init()`, `iolatency_init()`, `iolatency_exit()`.
- cgroup file handlers: `iolatency_set_limit()`, `iolatency_print_limit()`.
- blkcg policy hooks: `iolatency_pd_alloc()`, `iolatency_pd_init()`, `iolatency_pd_offline()`, `iolatency_pd_free()`, `iolatency_pd_stat()`.

## Important Behavior
On submission, the controller walks from the bio’s blkg up to root, checks whether each group needs scale updates, and acquires an in-flight slot. Root-issued or fatal-signal bios bypass sleeping but still increment inflight accounting.

On completion, it walks the same hierarchy, decrements inflight counts, records latency for configured groups, and periodically evaluates whether latency is within target. Rotational devices use mean latency statistics; SSDs use a simple missed/total percentile-like threshold.

When a protected group misses target, its parent’s `scale_cookie` is reduced so peers observe a scale-down event and lower `max_depth`. When conditions improve, the cookie scales back toward `DEFAULT_SCALE_COOKIE`; reaching default clears delay and restores unlimited depth.

## State and Synchronization
`struct blk_iolatency` holds the rq-qos object, enable timer, enable count, and async enable work. Each `iolatency_grp` has percpu latency stats, current window stats, `rq_wait`, `max_depth`, scale cookies, target latency, rolling average, and child latency coordination state.

Enabling or disabling issue-time tracking is deferred to workqueue context and performed with the request queue frozen to keep submission/completion in-flight accounting balanced.

## Risks
The hierarchy walk is intentionally disabled when no cgroup has a latency target; incorrect enable transitions could leak inflight counts. Scale-cookie propagation is distributed and can lag by design. Root-issued metadata/swap work is not counted the same way as ordinary cgroup I/O, so induced delay is essential to avoid priority inversion but can be hard to reason about.
