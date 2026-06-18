# sources/test-tools/stress-ng/stress-syncload.c

## Purpose
Implements the `syncload` stressor, which makes all workers generate synchronized CPU load spikes followed by synchronized sleeps. The busy phase rotates through small operations that touch instruction issue, scheduler yield, fences, atomics, vector math, RNG, writes, square root, and fused multiply-add paths depending on architecture and compile-time support.

## Important APIs, Types, And Functions
`stress_syncload_op_t` is the operation function pointer type. The operation table includes no-op, repeated NOPs, x86 pause, ARM/PPC yield, scheduler yield, x86 RDRAND fallback, memory fences, barriers, spin loops, optional vector math, nice calls, spin writes, sqrt, optional atomic increment of `g_shared->syncload.value`, and FMA-like updates to global arrays. `stress_syncload_init()` stores the shared start time. `stress_syncload_gettime()` reads it. `stress_syncload()` handles timing, operation rotation, sleep, and bogo increments. The exported info installs `.init = stress_syncload_init`.

## Control Flow
The init hook records a shared start timestamp before workers run. Each worker catches SIGILL, reads maximum busy and sleep milliseconds, converts them to seconds, checks x86 RDRAND support, initializes FMA state, waits at the global sync barrier, then loops. Each iteration selects the next operation from the compile-time-built table, extends the shared timeout by the busy duration, repeatedly calls the operation until the timeout, extends by the sleep duration, nanosleeps until the sleep timeout when still ahead of time, and increments bogo operations. Because workers use the same initial timestamp and deterministic duration progression, their bursts align.

## State And Persistence
State is in memory only. Shared state includes `g_shared->syncload.start_time` and optional atomic `value`; process globals include the RDRAND capability flag and arrays used to keep optimized math stores visible. No files or kernel objects persist beyond normal scheduling and timing effects.

## Dependencies And Integration Points
Depends on stress-ng shared-state layout, init hooks, timing, option parsing, sync barriers, signal handling, CPU feature detection, asm helpers for x86/ARM/PPC, compiler target clones, vector-math support, put helpers, scheduler/yield shims, nanosleep shim, and bogo counters. Compile-time feature gates determine the final operation table.

## Risks And Test Signals
Architecture-specific instructions can raise SIGILL if feature detection or target dispatch is wrong, so the signal catch is part of correctness. Synchronized wall-clock timing can drift under scheduler starvation, making actual burst alignment approximate. The global operation state is process-local except for the shared atomic value. Test signals are bogo progress across workers, visible periodic load spikes, no SIGILL-induced failure on supported CPUs, and option bounds enforcing 1 to 10000 millisecond busy/sleep windows.
