# sources/sync-backup/casync/src/cadigest.h

## Purpose

`cadigest.h` declares the public hash abstraction used throughout casync. It defines digest algorithm identifiers, exposes an opaque `CaDigest` handle, declares allocation/lifecycle/update/finalization helpers, and provides inline helpers for hashing fixed-width integers in little-endian byte order.

The header keeps callers independent from OpenSSL context details while preserving enough algorithm metadata for feature-flag negotiation, command-line parsing, and `CaChunkID` sizing.

## Important APIs, Types, and Constants

`CaDigestType` contains `CA_DIGEST_SHA256`, `CA_DIGEST_SHA512_256`, `_CA_DIGEST_TYPE_MAX`, `CA_DIGEST_DEFAULT = CA_DIGEST_SHA512_256`, and `_CA_DIGEST_TYPE_INVALID = -1`.

`typedef struct CaDigest CaDigest;` keeps implementation storage private to `cadigest.c`.

Lifecycle and allocation functions are `ca_digest_new()`, `ca_digest_free()`, `ca_digest_freep()`, and `ca_digest_ensure_allocated()`. The `ca_digest_freep()` inline helper is designed for the project cleanup attribute pattern, although it frees the pointed-to object without nulling the caller's slot.

Hash update and read APIs are `ca_digest_write()`, `ca_digest_write_u8()`, `ca_digest_write_u32()`, `ca_digest_write_u64()`, `ca_digest_read()`, and `ca_digest_reset()`. The integer helpers convert 32-bit and 64-bit values with `htole32()` and `htole64()` before hashing.

Metadata helpers are `ca_digest_get_size()`, `ca_digest_get_type()`, `ca_digest_get_name()`, `ca_digest_type_size()`, `ca_digest_type_to_string()`, `ca_digest_type_from_string()`, and `ca_digest_set_type()`.

## Control Flow Contract

Callers allocate a digest with a selected `CaDigestType`, write byte strings and integer fields in a stable order, then call `ca_digest_read()` to get the final result pointer. For reusable objects, callers call `ca_digest_reset()` before a new message or `ca_digest_set_type()` to change algorithms.

The integer helpers are part of the serialization contract: any cross-platform hash of structured numeric fields should use these helpers or equivalent little-endian encoding to avoid host-endian digest drift.

## State and Persistence Behavior

The header defines an in-memory handle only; it does not prescribe any on-disk format. Digest results are returned as borrowed pointers owned by the `CaDigest`.

The default algorithm is SHA-512/256. This default affects new digest users that select `CA_DIGEST_DEFAULT` directly or parse `"default"` through the implementation.

Because `ca_digest_freep()` does not clear `*d`, cleanup-style use is safe at scope exit, but manual calls followed by reuse of the same pointer would leave a dangling value unless the caller nulls it.

## Dependencies and Integration Points

The header includes `<stdbool.h>`, `<sys/types.h>`, and `<inttypes.h>`. The inline integer helpers require endian conversion macros such as `htole32()` and `htole64()` to be available through the platform or surrounding project headers.

It is included by `cachunkid.h`, `calocation.h`, `caformat-util.h`, cache/store/remote/seed code, encoder/decoder code, and the CLI. The digest type enum must remain aligned with feature-flag conversion helpers in `caformat-util` and with user-facing names in `cadigest.c`.

## Risks and Edge Cases

Changing `CA_DIGEST_DEFAULT` would affect chunk IDs and compatibility with existing archives, caches, remotes, and stores unless feature flags and migration logic are handled carefully.

The cleanup helper frees but does not null the pointer. That matches common cleanup-attribute usage but is a footgun for manual double-free-prone patterns.

The header exposes both raw byte writes and endian-normalized integer writes. Mixing host-endian raw integer writes with the helper-based format would create non-portable digests.

The digest read API returns `const void *` rather than a size-coupled object. Callers must pair it with `ca_digest_get_size()` or a known `CaChunkID` size and must not assume every supported algorithm returns the same length unless that remains an explicit project invariant.

## Test Signals

Header-level tests should compile translation units that include only `cadigest.h` and use all declared APIs and inline helpers. They should verify enum values for default and invalid cases where ABI or serialized behavior depends on them.

Behavioral tests should ensure `ca_digest_write_u32()` and `ca_digest_write_u64()` produce the same bytes on big-endian and little-endian hosts, either through cross-platform CI or explicit byte-order fixture tests.

Integration tests should verify that user-facing string names, feature-flag digest type mapping, `CaChunkID` size assumptions, and default digest selection remain synchronized across `cadigest.c`, `caformat-util`, and archive encoder/decoder paths.
