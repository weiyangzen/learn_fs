# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_thread.c

## Scope

This file implements the DragonFlyBSD LWKT per-CPU kernel thread scheduler: run queue management, thread allocation/caching, initialization, context switching, token release/reacquisition, preemption, yield paths, remote scheduling, CPU migration, priority management, and thread exit cleanup.

## Public And Internal APIs Covered

- Scheduler queues: `lwkt_schedule_self()`, `lwkt_deschedule_self()`, `lwkt_schedule()`, `lwkt_schedule_noresched()`, `lwkt_deschedule()`.
- Thread setup/lifecycle: `lwkt_gdinit()`, `lwkt_alloc_thread()`, `lwkt_init_thread()`, `lwkt_set_comm()`, `lwkt_hold()`, `lwkt_rele()`, `lwkt_free_thread()`, `lwkt_create()`, `lwkt_exit()`, `lwkt_remove_tdallq()`.
- Switching/preemption: `lwkt_switch()`, `lwkt_switch_return()`, `lwkt_preempt()`, `splz_check()`, `lwkt_maybe_splz()`.
- Yield and user-scheduler interaction: `lwkt_yield()`, `lwkt_yield_quick()`, `lwkt_user_yield()`, `lwkt_passive_release()`.
- Priority and clock handling: `lwkt_setpri()`, `lwkt_setpri_initial()`, `lwkt_setpri_self()`, `lwkt_schedulerclock()`.
- Migration: `lwkt_giveaway()`, `lwkt_acquire()`, `lwkt_setcpu_self()`, `lwkt_migratecpu()`, internal `lwkt_setcpu_remote()`.
- Panic/debug support: `crit_exit_wrapper()`, `crit_panic()`, `lwkt_smp_stopped()`.

## Control Flow And Behavior

- Each CPU owns a local LWKT run queue and all-thread queue. Remote CPUs schedule/deschedule via IPI rather than directly manipulating another live CPU's queues.
- `_lwkt_enqueue()` orders runnable threads by LWKT priority and user priority, scans from both head and tail to avoid degeneracy with large runnable sets, and requests reschedule if the inserted thread becomes queue head.
- `_lwkt_dequeue()` removes a runnable thread and clears `RQF_RUNNING` if the queue becomes empty.
- Thread structures and kernel stacks are cached through an objcache-backed `thread_cache`; `gd_freetd` preserves one exiting thread until it is safe to recycle.
- `lwkt_alloc_thread()` allocates or reuses a thread and stack, selects a CPU if none is specified, and calls `lwkt_init_thread()`.
- `lwkt_init_thread()` zeros and initializes core fields, installs a thread or spin message port, initializes pmap state, and inserts the thread into the target CPU's all-thread queue locally or by IPI.
- `lwkt_switch()` is the main scheduling loop. It releases current-thread user designation when needed, releases all held tokens before switching, avoids switching from hard interrupt/IPI context except panic/trap fallback, and chooses the next runnable thread or idle thread.
- Token contention is central to scheduling: candidate threads must reacquire their held tokens. Persistent contention eventually uses sorted token reacquisition and may skip to another runnable thread or the idle thread.
- Preempted threads are resumed before normal run-queue selection. Preemption chains use `td_preempted`, `TDF_PREEMPT_LOCK`, and `TDF_PREEMPT_DONE`.
- `lwkt_switch_return()` clears the old thread's running state, completes pending migration by IPI to the destination CPU, and signals exiting threads through `TDF_MP_EXITSIG`.
- `lwkt_preempt()` allows high-priority interrupt-support threads to directly run over the current thread only when critical-section depth, nesting, CPU ownership, token state, and preemption flags permit it.
- Yield helpers run pending soft interrupt work via `splz()` where allowed and switch only when reschedule conditions justify it.
- Remote scheduling uses `lwkt_schedule_remote()`; when invoked from an interrupt return frame it temporarily drops the IPI critical section so preemption can occur.
- Migration uses a pull/hand-off model. Current-thread migration deschedules itself, removes itself from the old CPU list, switches away, then finishes on the target CPU. Non-current migration waits for the old CPU to stop running/preempting the thread before changing `td_gd`.
- `lwkt_exit()` completes blocking cleanup first, waits for references to drain, removes the thread from queues, caches/freezes final resources, and exits via machine code.

## State And Data Structures

- Per-CPU state: `gd_tdrunq`, `gd_tdrunqcount`, `gd_tdallq`, `gd_idlethread`, `gd_curthread`, `gd_freetd`, `gd_reqflags`, `gd_spinlocks`, and indefinite wait diagnostics.
- Thread state: flags such as `TDF_RUNQ`, `TDF_RUNNING`, `TDF_MIGRATING`, `TDF_PREEMPT_LOCK`, `TDF_PREEMPT_DONE`, `TDF_EXITING`, `TDF_TSLEEPQ`, `TDF_ALLOCATED_THREAD`, `TDF_ALLOCATED_STACK`; priorities `td_pri`/`td_upri`; token stack; message port; CPU pointer; preemption links; migration target.
- Tunables/sysctls control spin-port debugging, scheduler debug, token contention spin loops, preemption enablement, and thread cache sizing.

## Dependencies

- Integrates with LWKT tokens, message ports, IPIs, critical sections, spinlocks, `splz`, user scheduler callbacks, pmap thread initialization, disk scheduler hooks, kernel stack VM allocation, objcache, and machine context switch handlers.
- Used by virtually all kernel execution contexts above early boot and interrupt trap glue.

## Risks And Invariants

- Queue operations must occur in the correct CPU's critical section; live foreign queue manipulation is routed through IPIs.
- Threads must not switch while holding spinlocks or while in hard interrupt/IPI context, except controlled panic/trap fallback.
- Tokens are released before a blocking switch and reacquired before resuming a thread; interrupts/IPIs must not run in the unsafe gap.
- Migration requires the thread to be descheduled and not running or preempt-locked before changing CPU ownership.
- Preemption deliberately rejects token-holding targets and heavily nested/current critical contexts to avoid corrupting scheduler invariants.
