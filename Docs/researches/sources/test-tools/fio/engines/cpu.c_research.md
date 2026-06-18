# sources/test-tools/fio/engines/cpu.c

Purpose: Implements the `cpuio` diskless/no-IO engine that burns CPU at a configured load, either by spinning or repeated qsort work.

Important APIs/functions: Registers one `ioengine_ops` named `cpuio`. Options are `cpuload`, `cpumode`, `cpuchunks`, and `exit_on_io_done`. Internal functions include `mwc32()`, qsort comparators, `do_qsort()`, `fio_cpuio_queue()`, `fio_cpuio_init()`, and cleanup/open callbacks.

Control flow: Init validates `cpuload`, clamps it to 100, temporarily sets setup runstate, configures thinktime so completed queue calls are interleaved with idle time, forces one pseudo file, and initializes either noop logging or qsort data. Queue optionally exits when other IO threads are done, then spins for `cpucycle` or runs qsort passes. In qsort mode, each work cycle measures elapsed time and recalculates thinktime to maintain requested CPU load.

State/persistence: Per-thread `cpu_options` stores load, mode, cycle, exit flag, and optional qsort data. Qsort data is allocated once and freed in cleanup.

Dependencies/integration: Uses fio engine registration, time helpers, runstate management, thinktime scheduling, and `fio_running_or_pending_io_threads()`.

Risks: `cpuload=0` is invalid, while very low loads can produce large thinktime. Qsort allocation is sizable and calibration may vary with CPU frequency/concurrency. `qsort_size` is static global but only used read-only.

Test signals: Run noop and qsort modes, validate load throttling behavior, cleanup under early termination, and `exit_on_io_done` with mixed jobs.
