# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_filling_bit_range.cpp

## Purpose
Tests `__ut_live_restore_fh_fill_bit_range`, which marks live-restore bitmap bits corresponding to byte ranges that have been filled in destination.

## Important APIs, Types, And Functions
`filling_data` stores `allocsize`, `nbits`, backing bitmap vector, and offset/length ranges. `is_bit_in_range` maps byte ranges to bit offsets, and `is_valid_bitmap` compares every bit against expected range membership. The test calls `__ut_live_restore_fh_fill_bit_range` under a write lock.

## Control Flow
The test creates a dummy `WTI_LIVE_RESTORE_FILE_HANDLE` with non-null source, initializes an rwlock, iterates through range scenarios, assigns bitmap state, fills each range, checks the bitmap, unlocks, and finally destroys the lock.

## State And Persistence Behavior
Only in-memory bitmap bits are modified. No real files are opened. The non-null source pointer ensures encoding/filling logic follows the live-restore source-backed path.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `mock_session`, WiredTiger bit-string sizing, and live-restore private helpers.

## Risks And Edge Cases
Covers single-slot ranges, multi-slot ranges, last-slot plus beyond-end ranges, fully out-of-range fills, entire bitmap fills, overlapping ranges, and varied allocsizes. It guards against off-by-one errors in `(offset + length - 1) / allocsize`.

## Test Signals
Every bit in the bitmap must equal expected range membership after filling. Any incorrect bit set/clear fails `is_valid_bitmap`.
