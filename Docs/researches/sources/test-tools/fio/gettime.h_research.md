# sources/test-tools/fio/gettime.h

Purpose: declares fio clock-source selection, timestamp retrieval, gettimeofday offload state, and local clock initialization APIs.

Important APIs/types/functions: defines `enum fio_cs` values `CS_GTOD`, `CS_CGETTIME`, `CS_CPUCLOCK`, and `CS_INVAL`; declares `fio_get_mono_time`, `fio_gettime`, `fio_gtod_init`, `fio_clock_init`, `fio_start_gtod_thread`, `fio_monotonic_clocktest`, `fio_local_clock_init`, `fio_gtod_set_cpu`; defines `struct fio_ts` with a `seqlock` and `timespec`; and provides inline `fio_gettime_offload`.

Control flow: callers normally call `fio_gettime`; the inline first checks `fio_ts`, reads a seqlock-protected timestamp until stable, and returns whether offload satisfied the request. Initialization functions are called during fio startup and per-thread setup.

State and persistence behavior: exposes the global `fio_ts` pointer. Timestamp state is process/shared-memory state, not durable persistence.

Dependencies/integration: includes architecture definitions and fio's seqlock. It is included by `fio.h` and timing users throughout fio.

Risks and test signals: all users depend on `fio_gettime_offload` being lock-free and returning consistent `timespec` pairs. Test signals include seqlock retry behavior under concurrent updates, null `fio_ts` fallback, and build coverage for architectures with/without CPU clocks.
