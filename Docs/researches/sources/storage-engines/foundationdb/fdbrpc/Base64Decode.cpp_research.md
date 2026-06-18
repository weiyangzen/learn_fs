# sources/storage-engines/foundationdb/fdbrpc/Base64Decode.cpp

## Purpose
`Base64Decode.cpp` implements regular padded Base64 and unpadded URL-safe Base64 decoding, arena-returning decode helpers, decoded-length calculations, and shared unit tests for both encode/decode implementations.

## Important APIs, Types, and Functions
Internal templates include `decodeValue<UrlDecode>`, `doDecode<UrlDecode>`, `getDecodedLength`, and `decodeStringRef<UrlDecode>`. Public functions are `base64::decodedLength`, `base64::decode` overloads, `base64::url::decodedLength`, and `base64::url::decode` overloads. Test helpers include `urlEncodedTestData`, `runTest`, and `transformBase64UrlToBase64`.

## Control Flow
Decoding maps input bytes through a 256-entry table, rejects illegal bytes as `_X`, and emits one to three plaintext bytes per group. Regular Base64 requires length divisible by four and strips up to two trailing `=` padding bytes before decoding. URL-safe Base64 accepts unpadded lengths except the invalid `4n+1` case. Arena decoders precompute output length, allocate in the supplied arena, call `doDecode`, and return an empty `Optional` on invalid input.

## State and Persistence Behavior
The implementation has no persistent runtime state. Arena decode failures may still leave allocated memory in the arena, as documented by the header. Unit-test data is static in the translation unit.

## Dependencies and Integration Points
It depends on `Base64Encode.h`, `Base64Decode.h`, Flow `Arena`, `StringRef`, `Optional`, `UnitTest`, deterministic randomness, and `fmt` for failure diagnostics. It integrates with fdbrpc utility code and tests both itself and the encoder.

## Risks and Edge Cases
Regular `decodedLength(int)` is a conservative estimate because padding is not known from length alone. The pointer-output API assumes callers allocated enough space. Whitespace and line-wrapped Base64 are rejected. Negative input lengths are not defended beyond integer pointer arithmetic expectations. URL-safe decoding intentionally rejects `=` padding.

## Test Signals
`/fdbrpc/Base64UrlEncode` and `/fdbrpc/Base64Encode` cover static vectors, random round trips, alphabet validation, URL-safe no-padding behavior, and regular padding behavior.
