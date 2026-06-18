# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_entropy.c

Read completely: 2855 lines.

Implements NetBSD's kernel entropy subsystem and legacy random-source compatibility API. The design centers on per-CPU entropy input pools, a global extraction pool, accounting for trusted entropy bits and timing samples, asynchronous consolidation, `/dev/random` readiness notifications, entropy source registration, on-demand source callbacks, and legacy `rnd(9)`/`rndio(4)` ioctls.

Core state:
- `struct entropy_cpu` holds each CPU's `entpool`, pending bit/sample counters, and drop/truncation/softint event counters.
- `entropy_global` (`E`) holds the global pool, entropy deficits, pending aggregate counts, epoch, select/kqueue waiters, source-list lock state, registered `krndsource` list, and seed/consolidation flags.
- `struct rndsource_cpu` keeps per-source per-CPU contributed bit/sample statistics and timer-delta estimator state.

Initialization and seeding:
- `entropy_init()` runs the `entpool` self-test, creates `kern.entropy.*` sysctls, initializes locks/CVs/select state, attaches the synthetic `seed` rndsource, allocates per-source/per-CPU state, and mixes early timer samples.
- `entropy_init_late()` establishes the entropy softint and starts the housekeeping thread `entbutler`.
- `entropy_seed()` validates a bootloader seed checksum with SHA1, handles byte-swapped/corrupt entropy counts, prevents double-counting repeated seeds, enters the seed, and zeroes it.
- `entropy_bootrequest()` requests entropy from all callback-capable sources before userland.

Entropy ingestion:
- `entropy_enter()` is the full non-interrupt path. It binds the LWP to the current CPU, enters data into the per-CPU pool, updates pending counters, then calls `entropy_account_cpu()` when consolidation may matter.
- `entropy_enter_intr()` is the interrupt/spin-lock path. It avoids blocking, drops samples if the per-CPU pool is busy, uses `entpool_enter_nostir()`, schedules the softint if stirring or accounting is needed, and only credits entropy if the whole sample fit.
- `entropy_softintr()` stirs the per-CPU pool after interrupt truncation and accounts pending entropy.
- Early boot uses `entropy_enter_early()` to enter data directly into the global pool under `splhigh()`.

Consolidation and readiness:
- `entropy_account_cpu()` performs immediate global transition when one CPU can satisfy the remaining bit deficit, otherwise aggregates pending counts and wakes the housekeeping thread when enough bits or samples exist across CPUs.
- `entropy_thread()` periodically checks `entropy_pending()` or waits for `E->consolidate`, then calls `entropy_do_consolidate()`.
- `entropy_do_consolidate()` broadcasts `entropy_consolidate_xc()` to extract each CPU pool into a temporary pool, mixes it into the global pool, decrements deficits, records timestamps, and calls `entropy_notify()`.
- `entropy_notify()` advances the entropy epoch, prints first readiness/best-effort messages, wakes CV waiters, and notifies poll/kqueue readers.
- `entropy_epoch()` and `entropy_ready()` expose reseed/readiness state to other kernel code.
- `entropy_reset()` handles VM clone/exposure-style resets by clearing pending counters on all CPUs and restoring maximum deficits.

Extraction and readiness APIs:
- `entropy_extract()` fills caller buffers from the global pool, optionally waiting, optionally failing hard, and warning/reresetting deficits when output is produced before full entropy. It supports the test-only `kern.entropy.depletion` mode.
- `entropy_poll()` and `entropy_kqfilter()` implement `/dev/random` style readiness for select/poll/kqueue. Readiness depends on either bit or sample deficit being zero unless depletion testing is active; writes are always ready.

Random source API and ioctls:
- `rnd_attach_source()`, `rnd_detach_source()`, and `rndsource_setcb()` manage kernel entropy sources and optional request callbacks.
- `rnd_add_data()`, `rnd_add_data_intr()`, `rnd_add_uint32()`, `_rnd_add_uint32()`, `_rnd_add_uint64()`, and `rnd_add_data_sync()` feed source data/timer samples through `rnd_add_data_internal()` and `rnd_add_data_1()`.
- Source flags honor `RND_FLAG_NO_COLLECT`, `RND_FLAG_NO_ESTIMATE`, `RND_FLAG_COLLECT_VALUE`, `RND_FLAG_COLLECT_TIME`, `RND_FLAG_ESTIMATE_TIME`, and `RND_FLAG_HASCB`; network sources default to no collection.
- `entropy_request()` serializes source callbacks with `rnd_lock_sources()` so detach cannot race callback traversal.
- `entropy_ioctl()` implements `RNDGETENTCNT`, `RNDGETPOOLSTAT`, source/stat enumeration by number or name, `RNDCTL` flag changes with reset/gather side effects, and `RNDADDDATA` user seed injection. Unknown legacy commands are forwarded through compatibility module hooks.

Concurrency and integration:
- Per-CPU pool access is protected by `entropy_cpu_get()`/`entropy_cpu_put()`, which block soft interrupts and preemption on the current CPU but deliberately allow hard-interrupt callers to drop samples instead of blocking.
- Global state is protected by `E->lock` after cold boot; selected counters are read with relaxed atomics for fast readiness checks.
- Source-list locking is separate (`E->sourcelock`) to allow callers to drop `E->lock` while invoking source callbacks.
- Integrates with sysctl, evcnt, softint, xcall, kthread, select, kqueue, kauth, module compatibility hooks, and the `entpool` cryptographic pool implementation.

Risks and notes:
- The code intentionally exposes only limited counters because event counters can become side channels.
- The timer entropy estimator is simple differential logic and only credits one sample, not bit entropy.
- `RNDCTL` can reset all pending entropy when collection/estimation is disabled for a trusted source.
- `RNDADDDATA` counts user-provided entropy only for privileged callers and only if a bootloader seed was not already counted.
- `entropy_extract()` can still fill buffers on shortage unless `ENTROPY_HARDFAIL` is set; callers are warned to use output only for CPRNG/DRBG seeding.
- Several comments flag policy concerns: writable sysctls at securelevel, readable deficit sysctls, legacy anonymous `rnd_add_data(NULL)`, and interrupt-context callers using the non-intr API.
