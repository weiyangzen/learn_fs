# sources/test-tools/fio/gettime.c

Purpose: fio's timing implementation. It selects and initializes clock sources, reads timestamps directly or through the offload cache, converts CPU clocks to nanoseconds, computes elapsed intervals in ns/us/ms/sec, and validates CPU-clock monotonicity across CPUs.

Important APIs/types/functions: exports `fio_get_mono_time`, `fio_gettime`, `fio_local_clock_init`, `fio_clock_init`, `ntime_since`, `ntime_since_now`, `utime_since`, `utime_since_now`, `mtime_since_tv`, `mtime_since_now`, `rel_time_since`, `mtime_since`, `time_since_now`, and `fio_monotonic_clocktest`. CPU-clock builds include calibration globals (`cycles_per_msec`, `clock_mult`, masks/shifts), TLS warning state, and clock-test structs.

Control flow: `fio_gettime` optionally logs caller sites in debug builds, returns the offloaded timestamp if `fio_ts` exists, otherwise dispatches by `fio_clock_source` to `gettimeofday`, monotonic `clock_gettime`, or CPU-clock conversion. `fio_clock_init` creates TLS keys when needed, calibrates CPU clock conversion, and may select `CS_CPUCLOCK` if TSC is marked reliable and the monotonic test passes. Calibration samples cycles per millisecond, trims outliers, computes multiplier/shift parameters, and records `cycles_start`. Elapsed helpers normalize signed sec/nsec or sec/usec differences and clamp unsigned variants to zero on time warp. The CPU monotonic test pins threads to CPUs, records ordered TSC samples using an atomic sequence, sorts them, and reports failures if TSC order goes backward.

State and persistence behavior: process-global timing state includes selected/inited clock source, CPU-clock calibration parameters, `tsc_reliable`, optional wrap warning state, debug caller hashes, and TLS data. No durable persistence.

Dependencies/integration: depends on fio architecture clock hooks, OS affinity helpers, `fio_sem`, `flist`, `hash`, math library, pthreads, and `gettime-thread` offload state. Timing APIs feed rate limiting, ETA, latency accounting, ramp period, sem timeout validation, and setup progress.

Risks and test signals: CPU-clock calibration and wrap handling are architecture-sensitive; offload timestamps use wall-clock `gettimeofday` while monotonic paths may use `CLOCK_MONOTONIC`; elapsed helpers silently clamp negative time for unsigned variants; and monotonic clock tests can be affected by CPU affinity masks. Tests should cover each clock source, forced unreliable TSC, CPU affinity masks, wrap-prone architectures, debug time logging, negative time deltas, and high-frequency `fio_gettime` overhead.
