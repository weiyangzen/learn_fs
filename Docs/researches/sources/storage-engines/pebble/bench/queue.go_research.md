# sources/storage-engines/pebble/bench/queue.go

## Purpose
`queue.go` builds a fixed-size queue workload used by the tombstone benchmark to continually delete old keys and insert new keys, creating point tombstone pressure.

## Important APIs, Types, And Functions
`QueueConfig`, `DefaultQueueConfig`, and `newQueueTest` are the main surfaces. `newQueueTest` returns a `Test` plus an atomic operation counter consumed by `RunTombstone`.

## Control Flow
Initialization fills `cfg.Size` MVCC-encoded queue keys, commits each with `NoSync`, and flushes. The run loop is a single goroutine that repeatedly deletes the current slot with `Sync`, waits on the optional limiter, inserts a new tail key/value with `Sync`, waits again, and increments the operation counter. Tick/done callbacks print instantaneous and cumulative queue ops/sec.

## State And Persistence Behavior
The workload persists an evolving queue keyspace in Pebble. Each cycle creates a point tombstone and a new key, and synchronous commits stress WAL/fsync behavior unless the surrounding config disables WAL elsewhere.

## Dependencies And Integration Points
It depends on `pebble`, `cockroachkvs`, `randvar`, atomics, and `RunTest` callback conventions. `tombstone.go` composes it with YCSB.

## Risks And Edge Cases
The queue slice and RNG are captured by a single worker; adding concurrency would require synchronization. The worker has no internal stop condition, relying on `RunTest` process-level duration/signal completion. Fatal errors abort the process.

## Test Signals
No direct tests. Runtime output and tombstone benchmark behavior are the main signals.
