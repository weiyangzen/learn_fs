# sources/storage-engines/wiredtiger/test/catch2/live_restore/unit/test_live_restore_bitmap_encode_decode.cpp

## Purpose
Tests live-restore bitmap hex encoding and decoding for several bitmap lengths, byte patterns, and an empty bitmap case.

## Important APIs, Types, And Functions
`test_data` stores expected hex string, bit count, and bitmap bytes. The test calls `__ut_live_restore_encode_bitmap`, `__ut_live_restore_decode_bitmap`, `__wt_readlock`, `__wt_readunlock`, `__wt_buf_free`, and live-restore `fs_open_file`.

## Control Flow
For each test bitmap, the test creates a source file large enough to produce the desired bitmap size, opens a live-restore file handle, manually assigns `bitmap` and `nbits`, encodes under the handle read lock, compares encoded hex for nonzero bitmaps, decodes back into the handle, compares bytes, closes the handle, removes files, deletes the test bitmap, and clears the buffer.

## State And Persistence Behavior
The bitmap is transient memory attached to the live-restore file handle. Encoding stores a hex string in a `WT_ITEM`; decoding replaces/initializes bitmap state based on encoded metadata. Files exist only to satisfy live-restore open semantics.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `mock_session`, `item_wrapper`, and live-restore bitmap helper functions exposed through unit-test wrappers.

## Risks And Edge Cases
Edge cases include zero bits, bit counts not divisible by eight, high/low nibble ordering, and ensuring encode is only decoded when `nbits != 0`, matching production behavior.

## Test Signals
The encoded string must match expected hex and decoded bytes must match the original bitmap for nonempty cases.
