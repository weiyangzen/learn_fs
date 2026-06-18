# sources/storage-engines/tikv/components/cdc/src/types.rs

## Purpose
`types.rs` currently defines the CDC connection identifier type used across service, watchdog, channel, and endpoint state.

## Important APIs, Types, and Functions
- `CONNECTION_ID_ALLOC: AtomicUsize` is the process-local monotonic allocator.
- `ConnId(usize)` is a copyable, hashable, debug-printable connection identifier.
- `ConnId::new` increments the allocator with `Ordering::SeqCst`.
- `Default` delegates to `new` so default construction still creates a unique ID.

## Control Flow
The only control flow is atomic fetch-add during connection creation. `Service::handle_event_feed` calls `ConnId::new` for every incoming event-feed stream, then passes that ID into channels, endpoint tasks, and watchdog logging.

## State and Persistence Behavior
The allocator is in-memory and resets on process restart. IDs are unique only within a single process lifetime and are not persisted or globally coordinated.

## Dependencies and Integration Points
The type is used by `service.rs`, `watchdog.rs`, endpoint task variants, downstream tracking, and CDC channel memory accounting/logging.

## Risks and Edge Cases
`usize` wraparound is theoretically possible in a very long-lived process, though practically remote. `SeqCst` is conservative and simple but stronger than strictly required for uniqueness.

## Test Signals
There are no local tests in this file. Coverage is indirect through service/watchdog tests that create and compare `ConnId`s, especially deregistration-on-watchdog-abort checks.
