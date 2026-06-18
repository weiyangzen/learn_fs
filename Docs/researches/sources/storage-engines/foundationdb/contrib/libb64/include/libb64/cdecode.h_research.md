# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/cdecode.h

## Purpose
`cdecode.h` declares the C streaming base64 decoder API and state type.

## Important APIs, Types, And Functions
`base64_decodestep` enumerates `step_a` through `step_d`. `base64_decodestate` stores the current step and a partially assembled plaintext character. Declared functions are `base64_init_decodestate`, `base64_decode_value`, and `base64_decode_block`.

## Control Flow
The header itself has no control flow. It defines the ABI contract consumed by `cdecode.c` and wrappers.

## State And Persistence Behavior
The state struct lets callers preserve decode progress across chunks. It is caller-owned and contains no allocated resources.

## Dependencies And Integration Points
It is included by `cdecode.c` and by the C++ wrapper in `decode.h` inside an `extern "C"` block. The include guard is `BASE64_CDECODE_H`.

## Risks And Edge Cases
The API does not expose required output-buffer sizing or strict validation semantics. `char plainchar` may hold partial binary data, so callers should treat it as opaque state.

## Test Signals
ABI tests should compile C and C++ consumers, initialize state, decode split inputs, and ensure repeated calls preserve state correctly.
