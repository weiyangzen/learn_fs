# sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.cpp

## Purpose
This file implements a public-domain SHA-1 digest class adapted to return the 20-byte binary digest as a `std::string`. It supports incremental updates from strings or streams and a convenience `from_string` one-shot helper.

## Important APIs, Types, And Functions
Public methods implemented here are `SHA1::SHA1()`, `update(const std::string&)`, `update(std::istream&)`, `final()`, and `from_string`. Private helpers are `reset`, `transform`, `buffer_to_block`, and `read`. The SHA-1 compression function is written with macros `SHA1_ROL`, `SHA1_BLK`, and the unrolled round macros `SHA1_R0` through `SHA1_R4`.

## Control Flow
Construction calls `reset()` to seed the five SHA-1 digest words. `update(string)` wraps the input in an `istringstream`; `update(stream)` fills the partial buffer up to 64 bytes, repeatedly converts the buffer into sixteen big-endian words, and calls `transform`. `final()` appends SHA-1 padding, conditionally transforms an extra block if the length field does not fit, appends the 64-bit bit length split across the last two words, transforms the final block, emits digest words in big-endian byte order, resets the instance, and returns the binary digest.

## State And Persistence Behavior
All state is in-memory: `digest[5]`, `buffer`, and `transforms`. `final()` is destructive in the useful sense that it resets the object for reuse after returning the digest. No persistent storage is touched.

## Dependencies And Integration Points
The implementation depends only on `SHA1.h`, `<sstream>`, and standard stream/string types. It can be used anywhere FoundationDB needs a compact local SHA-1 implementation without external crypto-library linkage.

## Risks And Edge Cases
SHA-1 is cryptographically broken for collision resistance and should not be used for security-sensitive signatures or integrity guarantees against malicious input. `read()` allocates a heap buffer for each read and does not use RAII, although it deletes on the normal path. The declaration and implementation use `uint32 block[BLOCK_BYTES]` for parameters where only `BLOCK_INTS` words are accessed; this is harmless for callers here but confusing. The returned digest is binary, not hex, and may contain NUL bytes.

## Test Signals
Known-answer tests for empty string, `"abc"`, multi-block inputs, stream updates split at 63/64/65 bytes, and object reuse after `final()` would cover the important paths. Tests should compare binary digest bytes, not printable strings.
