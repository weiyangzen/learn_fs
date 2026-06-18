# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpChecksum.hh

## Purpose
`XrdClHttpChecksum.hh` defines checksum type metadata and `ChecksumInfo`, the in-memory cache used by the HTTP plugin to store checksum values parsed from HTTP digest headers.

## Important APIs and Types
`ChecksumType` enumerates CRC32C, MD5, SHA1, SHA256, `kAll`, and `kUnknown`. `GetTypeString`, `GetChecksumLength`, and `GetTypeFromString` convert between enum values, wire strings, and raw byte lengths. `ChecksumEntry` stores one type/value pair using a fixed 32-byte array. `ChecksumInfo` provides `IsSet`, `Get`, `Set`, and `GetFirst`.

## Control Flow
Checksum parsing code populates `ChecksumInfo` through `Set`. Consumers request the preferred type via `IsSet`/`Get`; otherwise `GetFirst` iterates all real checksum slots up to `kAll` and returns the first populated value.

## State and Persistence
Checksum state is in memory only. Each checksum value is raw bytes, not hex text; formatting is done by operation code such as `CurlChecksumOp::Success`.

## Dependencies and Integration Points
This header is used by header parsing and checksum query operations. It intentionally has minimal dependencies: arrays, strings, and tuples.

## Risks and Test Signals
`Get` maps invalid `kAll`/`kUnknown` requests to the CRC32C slot and documents undefined data if unset, so callers must use `IsSet`. Tests should verify digest string conversion, byte lengths, first-set ordering, unknown input handling, and no out-of-bounds access as enum values evolve.
