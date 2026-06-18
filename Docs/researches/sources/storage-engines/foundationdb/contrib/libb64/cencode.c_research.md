# sources/storage-engines/foundationdb/contrib/libb64/cencode.c

## Purpose
`cencode.c` implements streaming base64 encoding from libb64.

## Important APIs, Types, And Functions
`CHARS_PER_LINE` is 72. `base64_init_encodestate` initializes `step_A`, `result`, and `stepcount`. `base64_encode_value(char)` maps six-bit values to the base64 alphabet or returns `=` for values above 63. `base64_encode_block` encodes an input chunk while preserving partial triples. `base64_encode_blockend` emits final padding and a trailing newline.

## Control Flow
Like the decoder, encoding uses a switch with intentional fallthrough. Steps A, B, and C consume one byte at a time, emit base64 characters from accumulated fragments, and save `result` and `step` when a chunk ends mid-triple. After every 18 four-character groups, it emits a newline. The block-end function emits `==`, `=`, or no padding depending on the saved step, then appends a newline.

## State And Persistence Behavior
Streaming state lives in `base64_encodestate`. The encoder writes into caller-provided output buffers and performs no allocation or persistence.

## Dependencies And Integration Points
It includes `libb64/cencode.h`, builds into `libb64`, and is wrapped by the header-only C++ `base64::encoder`.

## Risks And Edge Cases
The output buffer must be large enough for expansion, inserted newlines, padding, and final newline. `char` signedness can be surprising, but masks are applied before alphabet lookup. Consumers expecting unwrapped base64 must account for 72-character line wrapping and terminal newline.

## Test Signals
Tests should cover RFC vectors, chunk boundaries, empty input, one- and two-byte tails, line wrapping at 72 characters, and round trips through `cdecode.c`.
