# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_fill_hole.cpp

## Purpose
Tests `__ut_live_restore_fill_hole`, the live-restore background migration primitive that copies source bytes into destination for clear bitmap regions and marks them filled.

## Important APIs, Types, And Functions
`fill_hole_test` builds bitmap scenarios. `is_valid_fill` verifies destination bytes and bitmap bits for a single fill. `generate_bitmap` creates arbitrary bitmap states from integers, and `verify_fill_complete` validates complete migration. Tests call `__ut_live_restore_fill_hole`, `fh_read`, file-handle open/close, and WiredTiger bit helpers.

## Control Flow
The single-call section sets up source/destination files, attaches scenario bitmaps, locks the handle, calls fill-hole once, checks `finished`, `read_offset`, and filled data, then cleans up. The multiple-call section iterates many bitmap values, repeatedly calls fill-hole under a write lock until `finished`, then verifies all originally clear bits were copied from source and originally set bits stayed as destination dummy bytes.

## State And Persistence Behavior
The function mutates destination file contents and live-restore bitmap state. Source remains the authoritative data source for holes. `read_offset` tracks where a migration read occurred, and `finished` reports no clear bits remain.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore file handles, bit allocation/free, locking, and source/destination backing file operations.

## Risks And Edge Cases
Tests cover clear runs of length one, buffer-capped runs, clear runs to bitmap end, buffer smaller than allocsize, already-complete bitmaps, empty initial bitmaps, all-set bitmaps, and many pseudo-random bitmap shapes. It is sensitive to bit/byte offset conversion and preserving user-written destination regions.

## Test Signals
Expected filled length, `finished` state, `read_offset`, bitmap bits, and destination bytes must match. The complete pass requires no clear bits left and correct source/destination character provenance.
