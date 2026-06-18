# sources/storage-engines/foundationdb/fdbrpc/Base64Encode.cpp

## Purpose
`Base64Encode.cpp` implements one-shot regular Base64 encoding with `=` padding and URL-safe Base64 encoding without padding.

## Important APIs, Types, and Functions
Internal templates include `encodeValue<UrlEncode>`, `doEncode<UrlEncode>`, `getEncodedLength<UrlEncode>`, and `doEncodeWithArena<UrlEncode>`. Public functions are `base64::encode`, `base64::encodedLength`, `base64::encode(Arena&, StringRef)`, plus `base64::url` equivalents.

## Control Flow
The encoder consumes input in groups of three bytes and emits four 6-bit alphabet characters. For one or two trailing bytes, regular Base64 emits padding while URL-safe Base64 emits only the required unpadded characters. Arena helpers compute exact encoded length, allocate, encode, assert the actual length, and return a `StringRef`.

## State and Persistence Behavior
The implementation has no mutable persistent state. Encoded arena results live for the supplied arena lifetime.

## Dependencies and Integration Points
It depends on `Base64Encode.h` and Flow `Arena`/`StringRef` through the header. `Base64Decode.cpp` contains the test cases that validate this implementation.

## Risks and Edge Cases
The raw-buffer API assumes output capacity is at least `encodedLength(dataLength)`. Negative lengths are not guarded. The implementation intentionally does not line-wrap output and is not streaming. URL-safe output omits padding, so consumers expecting padded Base64 need the regular namespace.

## Test Signals
Round-trip unit tests in `Base64Decode.cpp` validate known vectors, random inputs, padding rules, and URL-safe alphabet constraints.
