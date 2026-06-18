# sources/storage-engines/wiredtiger/src/include/session.h

## Purpose
Defines `WT_SESSION_IMPL`, the central per-session internal state object, plus supporting structs/macros for data handle caches, hazard pointers, prefetch, error reporting, session-to-connection/btree/filesystem access, cursor sweeping, lock flags, operational flags, generation management, and operation tracking.

## Important APIs, Types, And Functions
- `WT_DATA_HANDLE_CACHE` stores per-session cached data handles in list and hash queues.
- `WT_HAZARD` and `WT_HAZARD_ARRAY` track pages protected from eviction, initially sized by `WT_SESSION_INITIAL_HAZARD_SLOTS`.
- `WT_PREFETCH` tracks sequential disk-read prefetch signals.
- `WT_ERROR_INFO` stores last API error, sub-error, message, and message buffer; constants define empty/success messages.
- `S2C`, `S2BT`, `S2BT_SAFE`, and `S2FS` map sessions to connection, btree, and active filesystem.
- Cursor sweep constants control cached cursor cleanup.
- `WT_SESSION_IMPL` includes public interface, event handler, session identity, operation timeouts, current data handle, bucket storage, handle/cursor caches, backup/compact/import/history-store/metadata tracking, lock callback state, scratch buffers, diagnostic thread checks, reconciliation/eviction timelines, transaction state, prefetch, checkpoint, operation handle lists, stats buckets, lock flags, operational flags, persistent-across-close RNG/hash/generation/stash/hazard/optrack state, and session stats.
- `WT_SESSION_CLEAR_SIZE` identifies the prefix cleared on session close/reuse.
- Generation constants classify checkpoint, eviction, snapshot, hazard, split, and commit generations.
- `WT_SESSION_FIRST_USE` tests whether hazard arrays have been initialized.
- `WT_READING_CHECKPOINT` detects open checkpoint handles.

## Control Flow
This header primarily defines layout and access macros. The session lifecycle clears fields up to `WT_SESSION_CLEAR_SIZE`, preserving RNG state, cached cursor/handle hash arrays, generation/stash/hazard memory, operation tracking fields, and stats as documented. Access macros assume `session->iface.connection` and `session->dhandle` are valid for their use cases.

## State And Persistence Behavior
`WT_SESSION_IMPL` is runtime state, but it coordinates persistent operations: current data handle, transactions, metadata tracking, checkpoint state, reconciliation/eviction timelines, backup cursors, import lists, and history-store cursors. Some memory persists past session close because other threads may still reference hazard/generation-protected memory; stash entries are released only when generations permit.

## Dependencies And Integration Points
Depends on almost every subsystem: connection, btree, filesystem, cursors, data handles, metadata, locks, transactions, checkpoint, cache/eviction/reconciliation, prefetch, backup, compact, import, operation tracking, stats, and diagnostics. It is the common context passed into most internal APIs.

## Risks
Because this struct is central and large, layout changes can affect session clearing, memory retention, diagnostics, and performance. `S2BT` requires a non-null data handle; misuse can crash. Session lock flags assume single-threaded session access. Persisted-after-close fields must not be accidentally cleared while other threads can observe them. Flag-space additions must stay within generated ranges and avoid collisions.

## Test Signals
Signals include session open/close/reuse tests, hazard pointer lifecycle, generation stash reclamation, cursor/handle cache sweeping, metadata transaction nesting, API timeout behavior, diagnostic single-thread checks, operation tracking buffers, checkpoint/eviction/reconciliation timeline capture, and flag-generation validation.
