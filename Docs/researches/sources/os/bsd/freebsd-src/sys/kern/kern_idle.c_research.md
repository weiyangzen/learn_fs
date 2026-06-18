# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_idle.c

## Purpose
Creates and initializes kernel idle threads during scheduler idle subsystem startup.

## Main Elements
- `SYSINIT(idle_setup, SI_SUB_SCHED_IDLE, SI_ORDER_FIRST, ...)` installs early idle setup.
- `idle_setup()` creates one idle kthread per CPU on SMP systems, or one idle thread on non-SMP systems.
- Each idle thread is created stopped via `kproc_kthread_add(sched_idletd, ...)`, marked runnable, flagged `TDF_IDLETD | TDF_NOLOAD`, assigned idle scheduler class, and given `PRI_MAX_IDLE`.
- The process backing idle threads is marked `P_IDLEPROC`.

## Dependencies And Integration
Integrates with scheduler entry `sched_idletd`, per-CPU state (`pc_idlethread` or `PCPU_SET(idlethread)`), kernel process/thread creation, and scheduler priority/class APIs.

## Risk Notes
The implementation intentionally avoids locking per-CPU idle-thread assignment because application processors should not be running yet. Any boot-order change that allows APs to observe idle thread state earlier would invalidate that assumption.
