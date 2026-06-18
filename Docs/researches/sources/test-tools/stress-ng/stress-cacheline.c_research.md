<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cacheline.c -->
# sources/test-tools/stress-ng/stress-cacheline.c

## Purpose
Implements the `cacheline` stressor, which coordinates multiple processes to pound different byte offsets in shared cache-line storage. It verifies that repeated adjacent, atomic, bit, copy, read/write, and width-varied access patterns do not corrupt the targeted byte while creating cache-line contention.

## Important APIs, Types, and Functions
`stress_cacheline_info` registers the stressor, `init`/`deinit`, `cacheline-affinity`, and `cacheline-method`. `stress_cacheline_method_t` maps method names to `stress_cacheline_func` callbacks. Methods include `adjacent`, `copy`, `inc`, `rdwr`, `mix`, `rdfwd64`, `rdrev64`, `rdints`, `bits`, and optional `atomicinc`. `get_L1_line_size()` queries CPU cache metadata, while `stress_cacheline_next_idx()` uses a shared lock to allocate even byte offsets.

## Control Flow
Initialization creates a shared lock and resets the global cacheline index. `stress_cacheline()` installs SIGCHLD handling, gets a unique offset, computes how many child processes are needed to span the L1 line size across instances, optionally forks helpers, synchronizes them, and runs `stress_cacheline_child()` in parent and children. Each child repeatedly invokes the selected method and may rotate CPU affinity. Parent increments bogo operations.

## State and Persistence Behavior
State lives in `g_shared->cacheline`: a shared buffer, index, size, and lock. Per-run child PID arrays are mmaped only when helper processes are needed. The stressor does not create persistent files. Cleanup kills/waits helper processes, unmaps PID storage, and destroys the lock in `deinit`.

## Dependencies and Integration Points
Depends on stress-ng shared memory, locking, sync PID helpers, CPU cache discovery, affinity helpers, random functions, and memory barriers. It integrates with stress-ng method option parsing and process-state reporting, and uses architecture-independent volatile memory accesses to force cache traffic.

## Risks and Edge Cases
Incorrect L1 line-size detection falls back to 64 bytes, which may under- or over-cover unusual hardware. Fork failures or PID mmap failures skip or reduce coverage. The methods assume the shared buffer has enough cacheline-sized storage and that byte offsets remain distinct. Optional affinity calls can fail under cpuset or permission limits.

## Test Signals
Good signals are startup logs showing process count and L1 line size, nonzero bogo progress, no "cache line error" failures, and clean child reaping. Run at least `--cacheline-method all`, one individual method, and `--cacheline-affinity` on a system with multiple CPUs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cacheline.c -->
