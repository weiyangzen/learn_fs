# sources/test-tools/stress-ng/stress-mlock.c

Purpose: `stress-mlock.c` exercises page locking and unlocking via `mlock`, optional `mlock2`, `munlock`, `mlockall`, and `munlockall`. It creates many small mappings, locks middle pages, unlocks and unmaps them, and probes invalid argument paths.

Important APIs/types/functions: `stress_mlock_pages` reads Linux `/proc/self/status` `VmLck` to track locked page count. `do_mlock` randomly chooses `mlock2` with `MLOCK_ONFAULT` or normal `mlock`, timing a sampled subset for metrics. `stress_mlock_max_lockable` derives the upper bound from `_SC_MEMLOCK`, `RLIMIT_MEMLOCK`, and `MLOCK_MAX`. `stress_mlock_misc` exercises invalid and unusual `mlock`, `munlock`, and `mlockall` calls. `stress_mlock_child` performs the main OOM-contained workload.

Control flow: `stress_mlock` delegates to `stress_oomable_child`. The child sizes and maps a pointer table, synchronizes, then repeatedly maps 3-page regions, tries invalid zero-length locks, locks the middle page, tags successful entries by setting the low bit in the page-aligned pointer, samples `/proc` locked-page counts, and increments bogo operations. It then unlocks tagged pages, tests bogus `munlock`, force-unmaps all regions, maps a second batch of single pages, calls `munlockall`, unmaps them, and repeats until `stress_continue`.

State and persistence behavior: all state is anonymous memory and kernel locked-page accounting. There is no filesystem persistence except optional `/proc` read access. Metrics accumulate nanoseconds per `mlock` and `munlock`; debug output can report max locked pages on Linux.

Dependencies and integration points: this stressor uses `core-madvise`, `core-mmap`, `core-out-of-memory`, memory limit helpers, lock/unlock shims, OOM wrappers, and metrics. It registers as `CLASS_VM | CLASS_OS` with `VERIFY_ALWAYS`; unsupported builds require `_POSIX_MEMLOCK_RANGE` and `HAVE_MLOCK`.

Risks: `RLIMIT_MEMLOCK`, capabilities, cgroup limits, and OOM pressure make `EAGAIN`, `EPERM`, and `ENOMEM` normal. The low-bit tagging scheme relies on page-aligned mmap pointers. `mlockall(MCL_FUTURE)` can affect later allocations if not followed by `munlockall`, so cleanup sequencing matters. Sampling `/proc/self/status` is Linux-specific and debug-only.

Test signals: run `stress-ng --mlock 1 --mlock-ops 1 --verify`, with and without `--oom-avoid`, and under small `RLIMIT_MEMLOCK`. Metrics should include nanoseconds per mlock call and, when unlocks occurred, nanoseconds per munlock call.
