# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_intr.c

## Role

Implements machine-independent interrupt management for DragonFlyBSD: hard interrupt and software interrupt registration, per-CPU interrupt thread creation, fast/slow interrupt dispatch, MP-lock handling for non-MPSAFE handlers, interrupt livelock mitigation, emergency interrupt polling, interrupt entropy registration, stray interrupt reporting, and interrupt count/name sysctls.

## Major Entry Points

- `register_swi()` and `register_swi_mp()` register software interrupt handlers on a selected/default CPU.
- `register_int()` registers hard or soft interrupt handlers, allocates records, creates emergency and normal interrupt threads as needed, updates fast/slow counts, sets MP-lock requirements, configures entropy, installs machine-level vectors, and updates soft interrupt lookup arrays.
- `unregister_swi()` and `unregister_int()` remove handler records, adjust fast/slow counts, teardown machine vectors when last handler leaves, clear MP-lock requirement if possible, update high-frequency flags, and free records.
- `sched_ithd_soft()`, `sched_ithd_hard()`, and virtual-kernel variants schedule interrupt threads.
- `ithread_fast_handler()` is called from vector code to run `INTR_CLOCK` fast handlers directly when possible, otherwise schedule the interrupt thread.
- `ithread_handler()` is the interrupt thread loop for normal dispatch, unmasking, randomness, and livelock state management.
- `ithread_emergency()` polls interrupt handlers at a sysctl/tunable-controlled rate for systems where normal interrupts are unreliable.
- `intr_init()` allocates the per-CPU/per-interrupt `intr_info` matrix and initializes IDs.

## Dispatch Model

- Each CPU/intr pair has an `intr_info` with a handler list, interrupt thread, random source state, count, running flag, fast/slow counts, flags, livelock state, and cpuid/intr identifiers.
- Fast interrupts are handlers marked `INTR_CLOCK`; slow handlers run through the interrupt thread.
- If any handler in a chain is not `INTR_MPSAFE`, the interrupt thread acquires the MP lock while processing the chain.
- Optional serializers can wrap handler calls with `lwkt_serialize_handler_call()` or try semantics for fast/emergency paths.
- `i_running` is only manipulated on the interrupt thread's CPU; remote scheduling uses IPIs.

## Livelock and Emergency Polling

- Livelock sysctls: `kern.livelock_limit`, `kern.livelock_limit_hi`, `kern.livelock_lowater`, and `kern.livelock_debug`.
- High-frequency interrupts can use the higher limit only when unshared.
- When an interrupt exceeds the per-second limit, the thread enters `ISTATE_LIVELOCKED`, a periodic systimer limits wakeups, and normal state resumes below low-water.
- Emergency polling is controlled by tunable/sysctl `kern.emergency_intr_enable` and `kern.emergency_intr_freq`, capped at 20000 Hz.

## Sysctls and Observability

- `hw.intrnames` emits slash-separated handler names per CPU/intr slot, defaulting to `irqN`.
- `hw.intrcnt_all` and `hw.intrcnt` emit interrupt counters for all CPU/intr slots.
- Stray interrupts are rate-limited and eventually silenced after repeated reports.

## File-System Relevance

- This is not VFS code, but block devices, storage controllers, network filesystems, timers, and device-backed files rely on this interrupt dispatch infrastructure.
- Interrupt randomness and livelock behavior can indirectly affect storage latency and kernel responsiveness under I/O-heavy workloads.

## Research Notes

- Registration migrates the current thread to the target CPU to initialize per-CPU structures and then migrates back.
- Handler records can become invalid after handler calls, so loops store `next` before dispatch.
- Invariant checks verify that interrupt handlers do not leak spinlocks, tokens, or MP locks.
