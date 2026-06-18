# File Research: sources/os/plan9/9front/sys/src/9/port/proc.c

Core portable process scheduler, process lifecycle, sleep/wakeup, notes, kernel processes, process accounting, and PID management.

Key responsibilities:
- Implements scheduler entry and context switching through `schedinit()`, `sched()`, `runproc()`, and `procswitch()`.
- Maintains priority run queues, CPU-usage decay, load average, affinity/wiring, and EDF integration.
- Handles preemption from clock/interrupt paths.
- Allocates/recycles `Proc` objects and initializes process state in `newproc()`/`procinit0()`.
- Implements `sleep()`, `tsleep()`, `wakeup()`, and `procinterrupt()` with rendezvous and qlock interruption handling.
- Manages notes: creation, posting to a process/group, delivery via `popnote()`, and broken-process retention.
- Implements process exit, wait records, child accounting, debugger wakeups, segment teardown, and PID release in `pexit()`.
- Creates kernel processes through `kproc()`.
- Provides process control for stop/trace/kill requests.
- Implements kernel error unwinding with `error()` and `nexterror()`.
- Tracks CPU/kernel time and load in `accounttime()`.
- Implements reference-counted PID table to avoid unsafe PID reuse on wraparound.

Important behavior:
- Scheduling can be delayed while locks are held, but only up to a threshold and not while holding critical allocator locks.
- `ready()` integrates EDF admission and priority recomputation, then enqueues by priority.
- `sleep()` sets `r->p` before checking the condition, then either backs out or commits the process to `Wakeme`.
- `procinterrupt()` can pull a process out of `sleep`, interruptible `eqlock`, or rendezvous wait.
- `pexit()` separates resource pointers under debug lock, frees them outside, then tears down segments and waits.
- PID entries outlive `Proc` references while parent/note IDs refer to them.

Notable risks:
- This file is concurrency-critical; many routines require specific interrupt level and lock ordering.
- `procflushmmu()` waits for other CPUs to observe MMU flush requests through clock interrupts.
- The PID hash uses fixed-size buckets; full buckets trigger retry with a different generated PID.
