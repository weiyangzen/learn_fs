# sources/storage-engines/pebble/db_internals.go

## Purpose
`db_internals.go` contains the small internal job ID utility used to identify asynchronous or background jobs such as flushes, compactions, and file ingestions. Job IDs are diagnostic and observability identifiers, not persisted correctness state.

## Important APIs, types, and functions
`type JobID int` is the exported identifier passed to event listener notifications and logs. `(*DB).newJobIDLocked` returns the current `d.mu.nextJobID` and increments it, requiring `DB.mu` to already be held. `(*DB).newJobID` is the locking wrapper for callers that do not already hold `DB.mu`.

## Control flow, state, and persistence
The control flow is intentionally simple: job ID allocation is serialized by `DB.mu`, and IDs are monotonically incremented in memory. There is no persistence across process restarts and no attempt to encode job identity into on-disk metadata.

## Dependencies and integration points
The functions depend on the `DB` struct's `mu.nextJobID` field defined in `db.go`. Allocated IDs are consumed by event listener calls, logging, WAL creation, flush scheduling, compaction scheduling, deletion jobs, and ingestion paths elsewhere in Pebble.

## Risks and invariants
The main invariant is that `newJobIDLocked` must only be called while holding `DB.mu`; otherwise duplicate or skipped IDs could occur under concurrency. Since IDs are not persisted or correctness-critical, overflow or restart reuse would mainly affect logs and event correlation, not data correctness.

## Test signals
There is no dedicated test in this file. Indirect coverage comes from tests in `db_test.go` that observe event listener behavior, tracing, compaction/flush scheduling, WAL rotation, and deletion cleanup. Those tests would expose severe job-ID allocation races mostly through inconsistent event correlation or unexpected panics.
