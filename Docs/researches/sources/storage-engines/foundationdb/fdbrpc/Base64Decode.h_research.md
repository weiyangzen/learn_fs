# sources/storage-engines/foundationdb/fdbrpc/Base64Decode.h

## Purpose
`Base64Decode.h` declares the fdbrpc Base64 decoding API for regular and URL-safe encodings.

## Important APIs, Types, and Functions
In namespace `base64`, it declares raw-buffer `decode`, conservative `decodedLength`, and arena `decode(Arena&, StringRef)`. In `base64::url`, it declares equivalent URL-safe functions whose decoded length can be exact or `-1` for invalid encoded lengths.

## Control Flow
The header has no executable control flow; it defines the API contract consumed by callers and implemented in `Base64Decode.cpp`. The contract distinguishes one-shot decoding from streaming and documents that no line wrapping is supported.

## State and Persistence Behavior
There is no state. Arena decode results are tied to caller-supplied arena lifetime, and invalid decode attempts may still consume arena memory.

## Dependencies and Integration Points
The header includes `<cstdint>` and `flow/Arena.h`, and exposes `StringRef`/`Optional`-based helpers for Flow code. It pairs with `Base64Encode.h` and the implementation tests in `Base64Decode.cpp`.

## Risks and Edge Cases
Callers of raw-buffer decode must size `plaintextOut` correctly. Regular Base64 requires padding-compatible length, while URL-safe Base64 omits padding and rejects `4n+1` lengths. The API is not streaming and does not accept wrapped MIME-style input.

## Test Signals
Coverage is supplied by the unit tests in `Base64Decode.cpp`, which exercise both regular and URL-safe decode declarations through round trips.
