# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_monitor.py

## Purpose
Tests the `Monitor` object used by Tahoe long-running operations for cancellation, status, completion state, and completion Deferreds.

## APIs / Types / Functions
- `Monitor`: `is_cancelled`, `raise_if_cancelled`, `cancel`, `get_status`, `set_status`, `is_finished`, `when_done`, `finish`.
- `OperationCancelledError` is expected after cancellation.

## Control Flow
Cancellation is checked before and after `cancel`. Status is set and read. Completion obtains an unresolved Deferred, calls `finish(300)`, validates returned/status/finished values, and asserts the Deferred fires with `300`.

## State And Persistence
All state is internal to a `Monitor` instance: cancellation flag, status value, finished flag, and Deferred waiters.

## Dependencies / Integration Points
Used by checker, repairer, upload, and download flows as a common operation-control primitive.

## Risks And Test Signals
Does not cover multiple `finish` calls or cancellation after finish. Passing tests prove the core monitor lifecycle and completion signaling work.
