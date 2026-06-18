# File Research: sources/teaching/xv6-public/proc.c

Implements process allocation, lifecycle, scheduling, sleep/wakeup, kill, and process dumps.

Key behavior:
- Maintains global process table under `ptable.lock`.
- `allocproc` finds an unused slot, assigns PID, allocates a kernel stack, builds trap frame and initial context returning through `forkret`/`trapret`.
- `userinit` creates the first user process running embedded `initcode`.
- `growproc`, `fork`, `exit`, and `wait` implement core Unix-like process operations.
- `scheduler` loops over runnable processes on each CPU, switching address spaces and contexts.
- `sched` validates scheduler invariants and switches back to CPU scheduler context.
- `yield` voluntarily returns CPU to scheduler.
- `forkret` releases `ptable.lock` and performs first process-context filesystem/log initialization.
- `sleep` atomically releases a caller lock and sleeps on a channel under `ptable.lock`.
- `wakeup`, `kill`, and `procdump` provide process wake/termination/debug support.

Important interactions:
- Uses per-CPU state from `proc.h` and APIC ID mapping.
- File descriptors and cwd are duplicated/dropped across fork/exit.
- Killed processes exit when returning to user mode or when awakened from sleep.
