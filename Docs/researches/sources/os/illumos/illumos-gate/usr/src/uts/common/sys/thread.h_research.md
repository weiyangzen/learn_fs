# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/thread.h

## Purpose
Defines the kernel thread object, thread states, scheduler/process flags, context operation hooks, active file descriptor tracking, wait-channel data, thread state manipulation macros, dispatcher locking helpers, stackinfo logging, and thread name support.

## Main Interfaces
- Thread states:
  - `TS_FREE`, `TS_SLEEP`, `TS_RUN`, `TS_ONPROC`, `TS_ZOMB`, `TS_STOPPED`, `TS_WAIT`
- Supporting structures:
  - `ctxop_t`: context save/restore/fork/lwp-create/exit/free hooks.
  - `afd_t`: per-thread active file descriptor table.
  - `lwpchan_t`: wait-channel uniqueness.
  - `kthread_id_t`, `kt_did_t`
- `kthread_t`: central kernel thread structure containing dispatch links, stack/PC, CPU binding, flags, scheduler state/priorities, PCB, wait channel, scheduling class data, fault state, locks, CPU/PIL/migration state, LWP/process/signal/audit/credential state, dispatcher lock pointer, syscall/post-trap flags, microstate profiling, turnstile priority inheritance state, TSD, doors, scheduler activation state, copyops, active fd table, sleep/wait queues, project/zone, taskq marker, DTrace state, user access state, wait mutex, name, and SMT-safety flag.
- Flag families:
  - `T_*` thread flags
  - `TP_*` process/LWP flags
  - `TS_*` scheduler flags
  - CPU/pset binding flags and helpers
- State/test macros:
  - `aston()`, `astoff()`
  - `ISTOPPED()`, `ISWAKEABLE()`, `ISWAITING()`, CPR variants
  - `VSTOPPED()`, `SUSPENDED()`, `INHERITED()`
  - priority and process/LWP conversion macros
- Kernel globals/functions:
  - `curthread`, `curproc`, `curproj`, `curzone`
  - `t0`, `pidlock`
  - thread free prevent/allow
  - priority-change helpers
  - `thread_transition()`, `thread_stop()`, `thread_lock*()`, `thread_onproc()`
  - stack init, thread naming
- State transition macros:
  - `THREAD_CHANGE_PRI()`, `THREAD_WILLCHANGE_PRI()`
  - `THREAD_RUN()`, `THREAD_WAIT()`, `THREAD_SWAP()`, `THREAD_ZOMB()`, `THREAD_ONPROC()`, `THREAD_SLEEP()`, `THREAD_FREEINTR()`
- Stackinfo constants and `kmem_stkinfo_t`.

## Dependencies And Relationships
Includes types, locks, LWP, time, signal, and KCPC headers. It is foundational for scheduler, process, syscall, DTrace, taskq, wait queue, and synchronization code.

## Research Notes
The structure is highly compatibility-sensitive inside the kernel. Comments document which fields are protected by thread locks, process locks, no locks, or current-thread-only modification rules.
