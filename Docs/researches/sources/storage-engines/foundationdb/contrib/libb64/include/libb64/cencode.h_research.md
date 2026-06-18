# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cencode.h

## Purpose
`cencode.h` declares the C streaming base64 encoder API and state type.

## Important APIs, Types, And Functions
`base64_encodestep` enumerates `step_A`, `step_B`, and `step_C`. `base64_encodestate` stores the current step, pending result bits, and line-wrapping step count. Declared functions are `base64_init_encodestate`, `base64_encode_value`, `base64_encode_block`, and `base64_encode_blockend`.

## Control Flow
The header contains declarations only. Runtime flow is implemented in `cencode.c`.

## State And Persistence Behavior
The caller owns `base64_encodestate` and output buffers. State enables chunked encoding and tracks line wrap cadence.

## Dependencies And Integration Points
It is included by `cencode.c` and by the C++ wrapper `encode.h` inside `extern "C"`. The include guard is `BASE64_CENCODE_H`.

## Risks And Edge Cases
The API requires callers to invoke `base64_encode_blockend` to flush padding. Output sizing is not encoded in the type system. Line wrapping is implicit through `stepcount`.

## Test Signals
Compile tests and chunked encoding tests should verify state initialization, finalization, padding, line wrapping, and C++ linkage compatibility.
