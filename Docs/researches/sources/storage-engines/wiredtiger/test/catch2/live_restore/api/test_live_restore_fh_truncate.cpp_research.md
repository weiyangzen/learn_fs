# sources/storage-engines/wiredtiger/test/catch2/live_restore/api/test_live_restore_fh_truncate.cpp

## Purpose
Tests live-restore `fh_truncate`, especially how truncation updates destination file size and marks bitmap bits for truncated ranges.

## Important APIs, Types, And Functions
`init_file_handle` opens a live-restore file and initializes `allocsize`, `nbits`, and `bitmap`. `validate_bitmap` uses `__bit_ffs` and `__bit_test` to assert that bits from the first truncated allocation slot onward are set. The test calls `fh_size`, `fh_truncate`, and `close`.

## Control Flow
The test creates a source file, opens the destination handle, confirms initial size, truncates to the same length, shrinks by two allocation slots, extends within the original length, extends beyond original length, clears the bitmap to simulate no migration, extends beyond bitmap with no bit changes, then shrinks partially within bitmap and validates marked bits.

## State And Persistence Behavior
Destination file length changes on each truncate. The live-restore bitmap marks truncated portions as filled so later reads do not fetch stale source bytes for deleted ranges. Extending beyond bitmap range does not mark unavailable bitmap bits.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, WiredTiger bit-string helpers, and the live-restore file-handle implementation.

## Risks And Edge Cases
Key edges are no-op truncate, shrink, growth after shrink, growth beyond original source-backed bitmap, a fully clear bitmap, and truncation partly inside tracked bitmap. The test assumes at least one set bit for `validate_bitmap`.

## Test Signals
Sizes must match requested truncation lengths, and bitmap validation must show expected first-set bit and all following bits set for shrunk ranges.
