# sources/test-tools/syzkaller/vm/dispatcher/pool.go

## Purpose

`pool.go` implements a generic, concurrent pool scheduler for bootable instances. It keeps a default runner active on unreserved instances while allowing a dynamically sized sub-pool for custom one-shot runners.

## Important APIs, Types, and Functions

Core abstractions are `Instance`, `UpdateInfo`, `Runner[T]`, `CreateInstance[T]`, `Pool[T]`, `Info`, `poolInstance[T]`, and `InstanceState`. Public methods include `NewPool`, `SetDefault`, `TogglePause`, `Loop`, `ReserveForRun`, `Run`, `Total`, and `State`. Internal helpers include `kickDefault`, `waitUnpaused`, `runInstance`, `reportBootError`, `reset`, `updateInfo`, `status`, `reserved`, `getInfo`, `reserve`, `free`, and `mergeContextCancel`.

## Control Flow

`Loop` starts one goroutine per slot. Each slot waits for the pool to be unpaused, creates an instance through `creator`, records boot time, then runs either its default job or a job received from the reserved job channel. When a job returns or creation fails, the loop recreates the instance. `ReserveForRun` stops and converts slots between default and custom-job modes. `Run` sends a wrapped job to the reserved job channel and waits for completion or context cancellation.

## State and Persistence Behavior

State is in memory: per-instance status, reservation flags, stop callbacks, job channels, boot average, and boot-error channel. `poolInstance.reset` preserves the reservation bit across restarts. No filesystem or external VM state is owned directly; the supplied creator and instance close functions manage that.

## Dependencies and Integration Points

It depends on Go generics, contexts, sync primitives, `pkg/stat`, and syzkaller logging. It is reusable infrastructure for managers that need a stable default workload plus reserved lanes.

## Risks and Test Signals

Concurrency correctness is the main risk: reservation changes race with booting/waiting instances, default replacement must restart active jobs, and boot errors must not deadlock when no reader drains the channel. `pool_test.go` exercises default restarts, split reserved pools, stress with pause/reserve/run, default replacement, pause behavior, run cancellation, and full boot-error channels.
