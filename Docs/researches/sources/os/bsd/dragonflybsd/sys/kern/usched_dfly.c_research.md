# File Research: sources/os/bsd/dragonflybsd/sys/kern/usched_dfly.c

## Purpose

`usched_dfly.c` implements DragonFly BSD's `dfly` user scheduler. It is a topology-aware evolution of the older BSD4 scheduler: instead of one global runqueue set, it maintains per-CPU runqueues, per-CPU aggregate load, CPU topology metadata, helper threads, and tunable heuristics for locality, IPC pairing, NUMA memory weighting, priority fairness, idle pulling, proactive pushing, and periodic rebalancing.

## Main Responsibilities

- Registers `struct usched usched_dfly`.
- Acquires and releases per-CPU current user LWP ownership for userland returns.
- Maintains per-CPU realtime, normal, and idle run queues.
- Tracks each LWP's queue CPU (`lwp_qcpu`), priority, estimated CPU, load contribution, fork state, and round-robin count through `lwp_usdata.dfly`.
- Chooses target CPUs by traversing the CPU topology tree and applying weighted load calculations.
- Updates per-CPU `uload` and `ucount` as LWPs become runnable, sleep, migrate queues, or exit.
- Implements scheduler-clock preemption, priority recalculation, and periodic balancing.
- Creates helper threads and exposes `kern.usched_dfly.*` sysctls.

## Data Model

Most scheduler constants and structures are defined in `sys/usched_dfly.h`, included by this file. Priorities use `MAXPRI == 128`, `NQS == 32`, and `PPQ == 4`. Normal priorities combine nice contribution (`NICE_QS` queues) and estimated CPU contribution (`EST_QS` queues). `ESTCPUMAX` is capped by `EST_QS`.

Each `struct usched_dfly_pcpu` contains:

- A per-CPU scheduler spinlock.
- A helper thread and `globaldata` pointer.
- Current user priority and current user LWP.
- Per-CPU aggregate `uload` and runnable/running `ucount`.
- Three queue arrays: normal, realtime/FIFO, and idle.
- Bitmaps for non-empty queues.
- Queue count, CPU id, CPU mask, and CPU topology node.

Global masks publish CPU availability: `dfly_curprocmask` for CPUs with current user LWPs and `dfly_rdyprocmask` for CPUs ready to accept work. Per-CPU flags mirror those masks to reduce global cache-line traffic.

## Core Control Flow

`dfly_acquire_curproc()` is called when a thread is about to return to userland. It has a fast path for the common case where the thread is not on a sleep queue, no scheduler action is pending, and it is already the CPU's `uschedcp`. The slow path removes sleep-queue state, recalculates CPU usage, handles pending reschedule requests, then loops until the LWP owns the current CPU's user scheduler slot.

During that loop it can:

- Move an outcast LWP to a CPU allowed by its CPU mask.
- Proactively push a rescheduled LWP to a better queue.
- Claim an idle `uschedcp` slot.
- Steal a slot from a much worse current user LWP.
- Requeue after an explicit yield.
- Move to another CPU under proactive push features.
- Fall back to descheduling itself, queueing, and switching.

`dfly_release_curproc()` clears `uschedcp` when the current LWP leaves user scheduling, updates the current mask unless the thread yielded, and calls `dfly_select_curproc()` to choose a replacement.

`dfly_select_curproc()` chooses the best LWP from the local CPU queue, marks the CPU current if needed, installs `uschedcp`, and schedules the target LWKT thread.

`dfly_setrunqueue()` chooses a target per-CPU queue for a runnable LWP. Forked LWPs get special placement according to feature flags: best CPU, same CPU, random/simple CPU, or current CPU when no local queue pressure exists. Non-forked LWPs normally use `dfly_choose_best_queue()`.

`dfly_setrunqueue_dd()` inserts the LWP into the chosen CPU queue and decides whether to interrupt the current user thread immediately, defer until the next scheduler tick, wake a local helper, or send a remote reschedule IPI.

## Priority, Load, and Accounting

`dfly_schedulerclock()` runs from the per-CPU scheduler timer. It handles contended idle-thread cases, increments per-LWP round-robin counts, triggers reschedule at `usched_dfly_rrinterval`, optionally respects `TDF_MP_BATCH_DEMARC`, increments `lwp_estcpu`, and calls `dfly_resetpriority()`.

`dfly_recalculate_estcpu()` recomputes estimated CPU use after enough scheduler ticks have elapsed. Sleeping LWPs decay by half and clear fast estimate state. Running LWPs update per-CPU accounting through `updatepcpu()`, compute instant CPU fraction from `lwp_cpticks / ttlticks`, and fold it into `lwp_estcpu`.

`dfly_resetpriority()` locks the LWP's queue CPU, maps `rtprio` plus nice/estcpu into `lwp_priority`, moves an on-runqueue LWP between buckets when its queue index changes, updates `td_upri`, recomputes `lwp_uload` with `lptouload()`, adjusts per-CPU aggregate load if the LWP is counted, and may request local or remote reschedule.

`dfly_uload_update()` adds an LWP's load to its queue CPU while its LWKT thread is runnable and removes it after the LWP sleeps. `dfly_exiting()` clears any remaining load contribution during LWP exit. `dfly_changeqcpu_locked()` changes queue CPU and moves load accounting when an LWP migrates between per-CPU queues.

`dfly_forking()` gives a child a worse initial `estcpu` according to `usched_dfly_forkbias`, marks it as forked for first placement, initializes `lwp_qcpu` from the parent subject to CPU mask, and docks the parent slightly to dampen fork-heavy workloads.

## Queue Selection and Rebalancing

`dfly_chooseproc_locked()` selects either the best or worst LWP from a CPU's queues. Best mode scans realtime, normal, then idle queues from lowest queue index. Worst mode scans idle, normal, then realtime from highest queue index. It respects `chklp` priority to avoid bouncing, checks CPU masks when pulling from another CPU, removes the chosen LWP, clears `LWP_MP_ONRUNQ`, and transfers queue/load ownership if the LWP is being stolen from another CPU.

`dfly_choose_best_queue()` is the main push heuristic. It walks from `root_cpu_node` down the topology tree, scoring child CPU groups by average weighted load. The score includes aggregate `uload`, `ucount * weight3`, priority availability (`weight4`), current CPU stickiness (`weight1`), NUMA memory advantage (`weight5`), and wake-from CPU pairing (`weight2`). IPC pairing can prefer or avoid SMT siblings or the same logical CPU depending on `ipc_smt`, `ipc_same`, and load average. The selected CPU is forced back into the LWP's allowed CPU mask if needed.

`dfly_choose_worst_queue()` is the pull heuristic. It walks the topology tree looking for the most overloaded nearby queue with runnable work, avoids returning the current CPU, and can ignore some stickiness when called by the periodic rebalancer.

`dfly_choose_queue_simple()` is the fallback when topology is unavailable. It scans ready CPUs from a rotating base, first preferring CPUs without current user LWPs, then CPUs with worse current priorities, and finally falls back to an allowed CPU.

`dfly_schedulerclock()` also contains the rover rebalancer for feature `0x04`. Every eight ticks, a rotating CPU can pull the worst LWP from the worst queue if the load difference justifies it, then either schedule it immediately or enqueue it locally.

`dfly_helper_thread()` runs per CPU at low priority. It marks the CPU ready, clears reschedule requests, schedules local queued work when available, and, under feature `0x01`, can steal a worst LWP from another overloaded CPU. It sleeps with a configurable poll timeout.

## Initialization and Tunables

`usched_dfly_cpu_init()` initializes the sysctl context, records highest NUMA node memory, locks configuration while per-CPU structures are initialized, creates helper threads, initializes queues, records CPU topology nodes, sets ready/current masks, and registers sysctls.

Key tunables include:

- `rrinterval`, `decay`, `poll_ticks`.
- `ipc_smt` and `ipc_same` for wake-from pairing.
- `weight1` through `weight7` for locality, IPC, queue count, priority availability, NUMA memory, and transfer hysteresis.
- `fast_resched`, `features`, and `swmask`.
- Debug sysctls `debug.dfly_scdebug`, `debug.dfly_pid_debug`, `debug.dfly_chooser`, and `debug.dfly_forkbias`.

Feature bits control idle pulling, proactive pushing, rebalancing rover, more proactive pushing, and fork placement mode.

## Concurrency and Risk Notes

This scheduler has many concurrent state transitions across per-CPU spinlocks, `lwp_spin`, atomic CPU masks, IPI callbacks, helper threads, and LWKT scheduling operations. Correctness depends on `lwp_qcpu`, `LWP_MP_ONRUNQ`, and `LWP_MP_ULOAD` staying synchronized with queue membership and per-CPU load counters. Several paths intentionally avoid global locks and accept benign races around current priorities or reschedule requests.

The topology heuristics are performance-sensitive and heavily tunable. Incorrect weights can cause thread migration instability, poor IPC locality, NUMA imbalance, or underuse of idle CPUs. The comments explicitly warn that fork bias and IPC/locality weights can strongly affect build workloads and multi-socket behavior.
