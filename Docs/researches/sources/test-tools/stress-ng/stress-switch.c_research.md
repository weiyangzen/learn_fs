# sources/test-tools/stress-ng/stress-switch.c

## Purpose
Implements the `switch` stressor, which forces rapid context switches between a parent worker and a child using one of several synchronization methods: POSIX message queues, pipes, or System V semaphores. It measures approximate nanoseconds per context switch and can optionally pace switching to a requested frequency.

## Important APIs, Types, And Functions
`stress_switch_method_t` maps method names to implementations. `stress_switch_rate()` reports harmonic-mean nanoseconds per context switch. `stress_switch_delay()` dynamically adjusts nanosleep delay based on bogo count and target frequency. `stress_switch_pipe()` writes through a pipe while a child drains it, optionally using `pipe2(..., O_DIRECT)` and pipe-size tuning. `stress_switch_sem_sysv()` ping-pongs a SysV semaphore with `SEM_UNDO`. `stress_switch_mq()` creates a POSIX message queue with depth one and exchanges fixed-size messages. `stress_switch()` selects the default `pipe` method, applies options, computes delay and threshold, and dispatches the selected method.

## Control Flow
Each method creates its IPC primitive before the global sync barrier, forks a child after sync, moves the child toward the parent's CPU, applies scheduler settings, and then enters a parent/child synchronization loop. The parent increments bogo operations on each exchange, optionally invokes rate pacing, and exits when the stress-ng stop condition or IPC failure occurs. The child loops on the complementary receive/send or semaphore operation until stopped or broken pipe/queue/semaphore failure. The parent records the metric, closes/unlinks/removes IPC resources, kills/waits the child, and deinitializes state.

## State And Persistence
State is transient IPC resources plus one child process per worker. Pipes are anonymous file descriptors. SysV semaphores persist in the kernel until `semctl(..., IPC_RMID)` and are therefore explicitly removed. POSIX message queues persist by name until `mq_unlink()`, so the stressor uses a name containing stressor name, parent PID, and instance and unlinks it on exit. Bogo counters and static delay adjustment state remain process-local.

## Dependencies And Integration Points
Depends on stress-ng affinity, kill/wait, mmap, signal, scheduler, sync-barrier, timing, metric, and option helpers. POSIX message queue support requires `mqueue.h`, librt, and `HAVE_MQ_POSIX`; SysV semaphore support requires `HAVE_SEM_SYSV` and `key_t`; pipe method is the unconditional fallback. It also integrates with stress-ng method-option enumeration through `stress_switch_method()`.

## Risks And Test Signals
IPC setup can fail because of mqueue limits, SysV semaphore limits, fork pressure, pipe buffer tuning failure, or missing compile-time features. SysV key generation retries only 100 random keys. The rate metric divides by the counted exchanges, so premature zero-count failures would make results unreliable. `switch-freq` pacing uses bogo count and wall time, which is approximate under heavy scheduling pressure. Test signals are child cleanup, IPC resource cleanup, bogo progress, nonzero nanoseconds-per-context-switch metrics for the selected method, and no lingering message queues or semaphores.
