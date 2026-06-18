# sources/storage-engines/pebble/compaction_scheduler.go

Purpose: Defines Pebble's experimental compaction scheduling interface and default `ConcurrencyLimitScheduler`, coordinating automatic/manual compactions with local or future global concurrency control.

Important APIs/types/functions: `CompactionScheduler` exposes `Register`, `Unregister`, `TrySchedule`, and `UpdateGetAllowedWithoutPermission`. `DBForCompaction` provides `GetAllowedWithoutPermission`, `GetWaitingCompaction`, and `Schedule`. `WaitingCompaction` carries optionality, priority, and score. `scheduledCompactionMap`, `manualCompactionPriority`, `noopGrantHandle`, `pickedCompactionCache`, and `ConcurrencyLimitScheduler` are the key implementation pieces.

Control flow: `Register` stores the DB and starts periodic granting. `TrySchedule` samples DB allowance and grants immediately if running compactions are below allowance. `Done` decrements running count and calls `tryGrantLockedAndUnlock`. Granting serializes through `isGranting`, samples allowance, calls `GetWaitingCompaction`, calls `Schedule`, and increments running count for accepted grants. `UpdateGetAllowedWithoutPermission` pokes the periodic granter when allowance rises.

State and persistence: All state is in memory: `runningCompactions`, `unregistered`, `isGranting`, `lastAllowedWithoutPermission`, channels, and the picked compaction cache's waiting/pc fields.

Dependencies and integration: Depends on `internal/base` grant-handle types and DB compaction internals. DB scheduling code uses the scheduler, while scheduler callbacks call back into the DB. Lock-order comments are part of the contract.

Risks: Deadlocks and over/under-granting are the main risks. Flushes can raise allowance without otherwise notifying the scheduler, so periodic granting and update pokes are important. The interface is explicitly experimental.

Test signals: Covered by deterministic scheduler datadriven tests for immediate grants, grant-on-completion, periodic granting, allowance update pokes, and unregister behavior.
