# sources/storage-engines/foundationdb/contrib/libb64/cdecode.c

## Purpose
`cdecode.c` implements streaming base64 decoding from the public-domain libb64 project.

## Important APIs, Types, And Functions
`base64_decode_value(int value_in)` maps ASCII characters in the `+` through `z` range to six-bit values, `-1` for ignored invalid characters, and `-2` for `=` padding. `base64_init_decodestate(base64_decodestate*)` resets a decoder to `step_a`. `base64_decode_block(code_in, length_in, plaintext_out, state_in)` decodes a chunk while preserving partial quartet state across calls.

## Control Flow
The decoder uses a switch with intentional fallthrough inside an infinite loop. At each step it reads input until a nonnegative decoded fragment appears or the input chunk ends. Steps `a` through `d` assemble output bytes by shifting and OR-ing fragments. On chunk exhaustion, the current step and partially built plaintext byte are saved into `state_in`.

## State And Persistence Behavior
Streaming state is stored in `base64_decodestate.step` and `plainchar`; callers own input and output buffers. No heap allocation or persistence occurs.

## Dependencies And Integration Points
It includes `libb64/cdecode.h` and is compiled into the `libb64` static target. The C++ `decode.h` wrapper delegates to this C API.

## Risks And Edge Cases
Invalid characters are skipped, which is permissive and may hide malformed input. Padding maps to `-2`, which is also skipped by the `fragment < 0` loops, so strict padding validation is not performed. Output buffer sizing is the caller's responsibility. The fallthrough style requires compiler warnings to tolerate implicit fallthrough.

## Test Signals
Tests should decode RFC 4648 vectors, chunked inputs split at every possible boundary, input with newlines/whitespace, padding cases, malformed characters, empty input, and output length correctness.
