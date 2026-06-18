# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_compute_read_end_bit.cpp

## Purpose
Tests `__ut_live_restore_compute_read_end_bit`, which determines the last contiguous clear bitmap bit that can be read from source in one migration/read operation.

## Important APIs, Types, And Functions
`compute_read_end_bit_test` builds a bitmap with a clear run and stores allocsize, nbits, buffer size, file size, and first clear bit. `is_valid_end_bit` independently computes the expected end bit using `WTI_BITMAP_END`, `WTI_BIT_TO_OFFSET`, `WTI_OFFSET_TO_BIT`, and `__bit_test`.

## Control Flow
For each scenario, the test creates a destination file of the scenario size, opens a live-restore file handle, attaches the bitmap and geometry, calls `__ut_live_restore_compute_read_end_bit`, validates the result with the independent implementation, closes the handle, and removes the file.

## State And Persistence Behavior
The bitmap is allocated in each scenario and attached to the handle. File size is real and constrains the maximum readable bit, modeling truncation and extension relative to bitmap length.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, live-restore private macros/helpers, and file-handle open behavior.

## Risks And Edge Cases
Covers single clear bit, clear runs capped by buffer size, clear runs to bitmap end, read size smaller than allocsize, file larger than bitmap, and file smaller than bitmap. It targets boundary mistakes in byte/bit conversions.

## Test Signals
`__ut_live_restore_compute_read_end_bit` must return zero and its end bit must match the independent scan bounded by bitmap end, read window, and file size.
