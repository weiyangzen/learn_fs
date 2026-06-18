# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_tick.c

This file implements scalable per-thread tick accounting. It is called by `clock()` every tick and either accounts ticks in the clock path or distributes work across CPUs with softints.

Core behavior:
- `clock_tick_init_pre()` initializes single-threaded mode, cache-line-aligned per-CPU tick structures, a shared softint if available, the global lock, and CPU-set partition descriptors.
- `clock_tick_init_post()` decides at boot whether to remain single-threaded or enable multi-threaded accounting based on CPU count, `clock_tick_threshold`, softint availability, and high-resolution tick settings.
- `clock_tick_mp_init()` populates online CPU tables and registers `clock_tick_cpu_setup()` for CPU online/offline updates.
- `clock_tick_cpu_setup()` maintains `clock_tick_cpus`, set boundaries, online CPU set, and set counts during CPU online/offline. Offline syncs softints where supported before removing a CPU from the online set.
- `clock_tick_schedule()` is called each tick. In single-threaded mode it rotates the scan start for fairness and directly calls `clock_tick_execute_common()`.
- In multi-threaded mode it batches pending ticks if previous softints are still active; otherwise it accounts the clock CPU immediately, schedules one softint per CPU set, rotates the scheduling CPU once per second, and clears the pending count.
- `clock_tick_schedule_one()` fills a target CPU’s per-CPU work descriptor and invokes its softint.
- `clock_tick_execute()` runs in softint context, drains pending work from the per-CPU descriptor, runs common accounting, and decrements `clock_tick_active`.
- `clock_tick_execute_common()` accounts the current CPU first to avoid losing a pinned thread, then scans assigned CPUs in rotating order.
- `clock_tick_process()` safely locates a CPU’s current thread, prevents thread free, avoids offline/quiesced/interrupt/idle threads, takes the persistent process lock pointer, checks migration/exiting races, and calls `clock_tick(t, pending)` once per lbolt.

Important invariants:
- Multi-threaded mode is chosen at boot only; CPU hotplug updates tables but does not switch accounting modes.
- `clock_tick_active` and `clock_tick_pending` batch missed ticks so busy systems charge multiple pending ticks in one `clock_tick()` call.
- `thread_free_prevent()` is needed because the current thread can otherwise be freed or recycled while inspected.
- `t_plockp` is used instead of dereferencing a possibly freed process to acquire `p_lock`.
- `t_lbolt < mylbolt` prevents double-accounting an LWP that migrates and appears in more than one CPU scan.
- CPU table updates are protected by `clock_tick_lock` and published with memory barriers.
