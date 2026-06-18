# sources/storage-engines/foundationdb/fdbrpc/Base64Encode.h

## Purpose
`Base64Encode.h` declares the fdbrpc Base64 encoding API for regular and URL-safe one-shot encoders.

## Important APIs, Types, and Functions
The regular namespace declares raw-buffer `encode`, exact `encodedLength`, and arena `encode`. `base64::url` declares the same shape for URL-safe output, replacing `+` and `/` with `-` and `_` and omitting `=` padding.

## Control Flow
The header only declares functions and documents behavior. It establishes that callers must use non-streaming, one-shot input and that no 72-character line wrapping is performed.

## State and Persistence Behavior
There is no state. Arena-returning overloads allocate output in caller-owned `Arena`.

## Dependencies and Integration Points
The header includes `<cstdint>` and `flow/Arena.h` and is consumed by Base64 utilities and tests in fdbrpc.

## Risks and Edge Cases
Raw-buffer callers must use `encodedLength` to avoid overflow. URL-safe and regular encodings are not interchangeable where padding or alphabet constraints matter.

## Test Signals
The implementation is validated by Base64 tests embedded in `Base64Decode.cpp`.
