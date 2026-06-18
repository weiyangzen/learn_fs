# sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/main.c

## Purpose
WT-4105 stresses small `WT_CURSOR::modify` updates against large documents while a snapshot transaction pins cache content, looking for modify hangs or cache pressure regressions.

## Important APIs, Types, and Functions
- Uses `WT_MODIFY`, `WT_ITEM`, two sessions, signal `alarm`, and a custom `WT_EVENT_HANDLER`.
- Table config uses huge key/value limits, small leaf pages, and 1 MiB memory pages.
- `on_alarm` aborts if a modify call exceeds the timeout.
- `handle_error` can suppress a small number of expected cursor API messages, though the main path does not set `ignore_errors`.

## Control Flow
The test opens a 1 GiB cache database, creates `table:large`, inserts two 1 MiB values, then begins a long-running snapshot transaction in the first session to pin cache. A second session repeatedly modifies both documents 1023 times, replacing 26 bytes at a moving offset. For non-sanitizer builds, each modify is guarded by a 15-second alarm. Offsets advance like an append sequence and wrap at document size.

## State and Persistence Behavior
The table contains two large values and many in-place logical modifies. One open snapshot transaction intentionally pins older cache state. Updates are committed in separate snapshot transactions in the second session. No explicit final verification is performed; success is absence of timeout/error.

## Dependencies and Integration Points
This test depends on modify support for row and column-store variants supplied by the smoke script. It integrates with sanitizer flags to disable alarms on slow instrumentation builds.

## Risks and Test Signals
The main signal is timeout or modify/transaction failure. Because verification is temporal rather than content-based, it catches performance/hang regressions more than data correctness. The connection config redundantly includes `statistics_log` twice, harmless but noisy.
