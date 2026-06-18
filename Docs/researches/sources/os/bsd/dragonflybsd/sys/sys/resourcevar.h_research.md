# File Research: sources/os/bsd/dragonflybsd/sys/sys/resourcevar.h

This header defines kernel-side resource state for profiling, per-process resource limits, per-UID accounting, and UID resource management APIs.

Key responsibilities:
- Defines `struct uprof` for process profiling state:
  - profiling buffer base/size
  - PC offset/scale
  - temporary address/tick fields for AST processing
- Defines `struct krate` for rate-limited kernel printing.
- Defines `struct plimit`, the copy-on-write process limit object:
  - `pl_rlimit[RLIM_NLIMITS]`
  - CPU limit cache in usec
  - cache-aligned spinlock and ref/exclusive word
- Defines `PLIMITF_EXCLUSIVE`, `PLIMITF_MASK`, and CPU-limit test results.
- Defines per-CPU `struct uidcount` with POSIX-lock and open-file counters.
- Defines `PUP_LIMIT` rollup threshold of +/-32 for UID per-CPU counters.
- Defines `struct uidinfo` for per-UID consumption:
  - socket buffer bytes
  - process count
  - POSIX lock and open-file rollups
  - variant symlink set
  - per-CPU counters
  - cache-aligned reference count
- Declares kernel APIs for profiling, rusage aggregation, UID accounting, UID object lifecycle, and process limit lifecycle/modification.

Important invariants:
- `struct plimit` is designed for sharing after fork and copy-on-write modification.
- `p_refcnt` is separated into its own cache-aligned area to avoid cacheline churn on mostly read-only limit data.
- Threaded programs cache `p_limit` in thread state for lockless reads.
- Per-CPU UID counts intentionally allow small slop to avoid cacheline ping-ponging.
- `PLIMIT_TESTCPU_*` distinguishes OK, soft-limit `SIGXCPU`, and hard kill outcomes.

Research notes:
- This header is internal resource-accounting infrastructure rather than user ABI.
- It ties resource limits to DragonFly-specific spinlocks, varsym sets, and per-CPU UID rollups.
