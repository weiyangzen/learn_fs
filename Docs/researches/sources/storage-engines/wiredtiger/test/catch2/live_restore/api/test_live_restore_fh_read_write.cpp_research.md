# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_read_write.cpp

## Purpose
Tests live-restore `fh_read` and `fh_write` selection between source and destination backing files, including partially migrated pages and writes beyond the tracked bitmap range.

## Important APIs, Types, And Functions
`init_file_handle` opens a live-restore data file, configures `allocsize`, `nbits`, and allocates `bitmap` with `__bit_alloc`. The test uses `WTI_LIVE_RESTORE_FILE_HANDLE::iface.fh_read/fh_write`, direct `destination->fh_read`, direct `source->fh_read`, and helper file creation/removal.

## Control Flow
With a source file present, the test first verifies reads come from source before migration. It simulates background migration by writing source bytes to destination for a non-page-aligned length, then checks full migrated pages, one partial page, user writes that override destination without modifying source, and writes partially or completely beyond the bitmap. A second section removes the source, confirms writes/readbacks operate only on destination, and verifies `source == nullptr`.

## State And Persistence Behavior
The bitmap records which allocation slots have been written/migrated. Destination contents change for simulated migration and user writes; source contents remain unchanged in the source-present section. Writes past the original bitmap extend destination-visible data without source involvement.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `live_restore_test_env`, WiredTiger bit operations, and the live-restore file-handle implementation. It interacts with source/destination handles beneath the wrapper to verify physical backing contents.

## Risks And Edge Cases
Important edge cases are page-size larger than allocsize, file size not divisible by page size, partial migration inside a page, missing source, writes crossing bitmap end, and writes wholly beyond bitmap end. The test assumes manual bitmap sizing matches `file_size / allocsize`.

## Test Signals
Expected vectors of source, dummy, and written characters must match both wrapper reads and underlying destination/source reads. Source mutation, wrong fallback source/destination selection, or mishandled out-of-bitmap writes fail the test.
