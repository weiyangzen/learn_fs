# sources/storage-engines/raft-engine/src/event_listener.rs

## Purpose
Defines extension callbacks for observing important raft-engine internal file and memtable events.

## Important APIs, Types, And Functions
`EventListener` is a `Sync + Send` trait with default no-op methods: `post_new_log_file`, `on_append_log_file`, `post_apply_memtables`, `first_file_not_ready_for_purge`, and `post_purge`.

## Control Flow
Engine and pipe-log components call listeners around file creation, log append, memtable application, purge readiness decisions, and post-purge notifications. Callers may install multiple listeners; engine open also appends a purge hook listener.

## State And Persistence Behavior
The trait itself is stateless. Implementations may maintain external state that affects purge behavior through `first_file_not_ready_for_purge`, making listener correctness relevant to durable file deletion timing.

## Dependencies And Integration Points
Uses `FileBlockHandle`, `FileId`, `FileSeq`, and `LogQueue` from pipe-log types. Integrated with `Engine::open_with`, write apply callbacks, and purge manager/file pipe log hooks.

## Risks And Edge Cases
Callbacks may run under different locks or threading contexts, including global queue locks, so implementations must avoid blocking or re-entering engine APIs unsafely. A conservative `first_file_not_ready_for_purge` can retain files indefinitely; an incorrect permissive one can allow premature deletion.

## Test Signals
Purge hook behavior, managed deletion/reuse tests, and listener-based integration tests elsewhere are the main signals.
