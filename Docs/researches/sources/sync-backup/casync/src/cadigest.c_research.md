# sources/sync-backup/casync/src/cadigest.c

## Purpose

`cadigest.c` implements the `CaDigest` abstraction declared in `cadigest.h`. It wraps OpenSSL SHA-256 and SHA-512 contexts behind a small casync-specific API, normalizes digest sizes to `CaChunkID` length, supports the project default SHA-512/256 variant, and provides string conversion helpers for digest type selection.

The module is used anywhere casync needs stable content or metadata hashes: chunk ID generation, location IDs, archive/payload/hardlink digests in encoder and decoder code, cache validation, store validation, remote validation, and command-line digest option parsing.

## Important APIs, Types, and Functions

The private `struct CaDigest` stores a `CaDigestType`, a result buffer large enough for either SHA-256 or SHA-512 output, and a union of `SHA256_CTX` and `SHA512_CTX`.

`ca_digest_new()` validates the requested type, allocates the object, stores the type, and initializes the OpenSSL context via `ca_digest_reset()`. `ca_digest_free()` uses the project `mfree()` helper and accepts `NULL`.

`ca_digest_reset()` initializes the active hash context. SHA-256 uses `SHA256_Init()`. SHA-512/256 uses `SHA512_Init()` and then writes the SHA-512/256 initial hash values directly into the OpenSSL `SHA512_CTX` words because the code predates or avoids a native OpenSSL SHA-512/256 API.

`ca_digest_write()` updates the active context, ignoring `NULL` digest handles and zero-length writes but asserting a non-NULL buffer for positive lengths.

`ca_digest_read()` finalizes the active context into `result` and returns a pointer to that buffer. For SHA-512/256 it finalizes a full SHA-512 result but callers use `ca_digest_get_size()` or fixed `CaChunkID` copies to consume the first 32 bytes.

Query and conversion helpers include `ca_digest_get_size()`, `ca_digest_get_type()`, `ca_digest_get_name()`, `ca_digest_type_size()`, `ca_digest_type_to_string()`, `ca_digest_type_from_string()`, `ca_digest_ensure_allocated()`, and `ca_digest_set_type()`.

## Control Flow

A typical caller creates or ensures a digest object, writes byte ranges in deterministic order, finalizes with `ca_digest_read()`, and copies `ca_digest_get_size()` bytes or a `CaChunkID`-sized prefix. Reuse requires `ca_digest_reset()` before writing a new stream. Type changes go through `ca_digest_set_type()`, which validates the type and resets the new context.

`ca_digest_ensure_allocated()` is a lazy allocation helper used by encoder/decoder digest paths. If the pointer already contains a digest, it returns `0` without checking or changing the existing type. If the pointer is `NULL`, it allocates the requested type and returns `1`.

String conversion is table driven. `"default"` maps to `CA_DIGEST_DEFAULT`, and explicit names are `"sha256"` and `"sha512-256"`.

## State and Persistence Behavior

Digest state is fully in memory. The OpenSSL context accumulates bytes until reset or finalization. `ca_digest_read()` is destructive in the normal OpenSSL sense: it finalizes the current context, so additional writes after a read are not a valid continuation unless the context is reset first.

The result pointer returned by `ca_digest_read()` is owned by the `CaDigest` object and remains valid only until the next reset, read, type change, or free. The code does not persist digest output to disk.

The SHA-512/256 implementation mutates OpenSSL internal context fields after `SHA512_Init()`. That is stable only for OpenSSL versions exposing the same `SHA512_CTX` layout through the included headers.

## Dependencies and Integration Points

The direct dependency is OpenSSL `<openssl/sha.h>`. Project dependencies are `cadigest.h` for declarations and `util.h` for allocation, equality, and assertion helpers.

Integration points include `cachunkid.c` for one-shot chunk IDs, `calocation.c` for location hashing with little-endian integer writes, `caencoder.c` and `cadecoder.c` for archive/payload/hardlink digests, `caseed.c` for seed chunk hashes, `cacache.c`, `castore.c`, and `caremote.c` for validation digests, and `casync-tool.c` for user-facing digest type parsing and display.

## Risks and Edge Cases

`ca_digest_read()` finalizes the context but does not mark it finalized. A caller that reads twice or writes after reading without a reset relies on undefined or OpenSSL-specific behavior. Tests should treat digest objects as single-use between resets.

`ca_digest_ensure_allocated()` does not verify that an existing digest has the requested type. Callers that change feature flags or expected digest algorithms while reusing a pointer must call `ca_digest_set_type()` themselves.

The SHA-512/256 implementation depends on direct access to `SHA512_CTX.h[]`, which can break with OpenSSL API opacity or provider-only implementations. It also finalizes a 64-byte SHA-512 buffer while reporting a 32-byte digest size, so every caller must honor the reported size.

Digest functions generally return errno-style errors for allocation/type problems but `ca_digest_write()` and `ca_digest_reset()` are void and silently ignore `NULL` digest pointers. This is convenient for optional digests but can hide missed initialization when the caller expected hashing to be active.

## Test Signals

Unit tests should compare SHA-256 and SHA-512/256 results against known test vectors, including empty input and multi-write input. SHA-512/256 should specifically verify the 32-byte prefix returned by `ca_digest_get_size()`.

Lifecycle tests should cover invalid types, `NULL` return pointers, `ca_digest_ensure_allocated()` returning `1` on allocation and `0` on existing digest, `ca_digest_set_type()` resetting the stream, zero-length writes having no effect, and `ca_digest_type_from_string()` handling `"default"`, explicit names, unknown names, and `NULL`.

Integration tests should verify that `CaChunkID` generation, encoder/decoder archive digest, payload digest, hardlink digest, and location hashing all copy only the expected digest length and remain stable across architectures through the little-endian helpers in the header.
