# sources/test-tools/stress-ng/stress-workload.c

## Purpose
Implements `workload`, a scheduler/OS stressor that schedules synthetic work bursts inside configurable time slices to exercise timing, scheduler policy, optional pthread fan-out, POSIX message queues, and `core-workload` methods.

## Important APIs, types, and functions
`stress_workload()` is the entry point. `stress_workload_t` stores scheduled offset and run duration; `stress_workload_bucket_t` records observed start-offset histograms. `workload_dists[]` exposes cluster, even, poisson, random1, random2, and random3. `stress_workload_set_sched()` applies optional scheduler policy. `stress_workload_exercise()` generates/sorts work items, sleeps/yields to scheduled offsets, accounts buckets, and calls `stress_workload_waste_time()` or dispatches to worker threads.

## Control flow
The stressor reads settings, warns if quanta are below timer slack, maps a shared buffer, optionally creates a POSIX mqueue and pthread workers, validates quanta versus slice, allocates work items, initializes buckets, applies scheduler policy, synchronizes, then repeatedly runs scheduled workload slices. Cleanup reports histogram, cancels/joins threads, closes/unlinks mqueue, frees work items, and unmaps the buffer.

## State and persistence
State includes mapped buffers, heap workload array, histogram counters, optional static thread descriptors, and a POSIX message queue that is unlinked on cleanup. No repository files are written.

## Dependencies and integration points
Registered as `stress_workload_info` with `CLASS_SCHEDULER | CLASS_OS`, options for distribution/load/method/quanta/scheduler/slice/threads, and `VERIFY_ALWAYS`. Depends on scheduler helpers, `core-workload`, mmap/madvise, pthreads, POSIX mqueues, timing, sorting, and debug output.

## Risks and edge cases
Threaded mode requires pthread, librt, POSIX mqueue, and headers; otherwise it falls back to single-process mode. Real-time scheduling may fail without privilege and is tolerated. `workload-quanta-us > workload-slice-us` is a hard failure. Timing quality depends on timer slack, load, scheduler policy, and waste method.

## Test signals
Bogo counts scheduled quanta. Instance zero reports thread count and start-time histogram. Resource signals include mmap, mqueue, pthread, and calloc failures.
