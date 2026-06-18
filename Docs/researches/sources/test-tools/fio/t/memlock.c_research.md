# sources/test-tools/fio/t/memlock.c

## Purpose
Memory pressure utility that allocates a configured MiB amount per thread and repeatedly touches pages, useful for exercising memory locking, page residency, or system pressure scenarios.

## Important APIs, Types, and Functions
`struct thread_data` holds MiB per thread. `worker()` allocates `mib * 1024 * 1024`, loops 100000 times, and writes 512 bytes at offset 512 of each 4 KiB page. `main()` parses MiB and thread count, creates pthreads, and joins them.

## Control Flow
The main thread validates arguments, allocates the pthread array, stores the shared MiB value, starts all workers with the same `td`, then waits for completion. Each worker prints one message after its first full pass.

## State and Persistence Behavior
No files are written. Runtime state is large heap allocation per worker and CPU time spent dirtying memory.

## Dependencies and Integration Points
Uses pthreads and libc allocation/memset. It is independent of fio internals despite living in the test tree.

## Risks
`malloc()` is not checked before use. Very large MiB/thread values can exhaust memory or trigger OOM. The fixed 100000 passes can run for a very long time. All workers share one immutable `td`, which is safe for current fields but would not be for mutable additions.

## Test Signals
Signals are successful allocation/startup and visible first-pass output for each thread. External monitoring can observe memory pressure or locking behavior.
