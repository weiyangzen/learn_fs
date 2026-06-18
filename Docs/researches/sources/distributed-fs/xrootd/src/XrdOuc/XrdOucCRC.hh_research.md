# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.hh

## Purpose
Declares the `XrdOucCRC` static utility class for CRC32 and CRC32C calculation and verification.

## Important APIs and types
`CRC32()` is the legacy CRC-32 entry point. `Calc32C()` has scalar and page-vector overloads; scalar supports incremental continuation via `prevcs`, while vector mode fills one checksum per page. `Ver32C()` overloads verify scalar checksum, identify first failing page, produce per-page booleans, or return computed page checksums.

## State, dependencies, and integration
The class stores a private static `crctable[256]` for legacy CRC32. It depends on `XrdSys::PageSize` for page splitting and `<cstdint>` for fixed-width checksum types.

## Risks and test signals
The API is static and has no synchronization needs beyond the underlying CRC32C implementation. The main contract risk is vector sizing by callers. Unit tests should compile all overloads, check known vectors, and verify final partial-page behavior.
