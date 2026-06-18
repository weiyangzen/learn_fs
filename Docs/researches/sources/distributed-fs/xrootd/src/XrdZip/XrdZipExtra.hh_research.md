# sources/distributed-fs/xrootd/src/XrdZip/XrdZipExtra.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipExtra.hh` defines the ZIP64 extended information extra field used by XRootD ZIP support. It stores 64-bit compressed/uncompressed sizes, local-header offset, and disk number when classic ZIP fields overflow. The source was read as a complete 183-line file.

## Important APIs, Types, and Functions

`struct Extra` has constructors from file size, from another `Extra` plus central-directory offset, and default zero initialization. `Find()` scans an extra-field byte region for header ID `0x0001`. `FromBuffer()` validates header ID and expected data size, then conditionally reads fields according to overflow flags. `Serialize()` writes the header and included 64-bit fields when `totalSize > 0`. `enum Ovrflw` defines `NONE`, `UCMPSIZE`, `CPMSIZE`, `OFFSET`, and `NBDISK`. Stored fields are `dataSize`, `uncompressedSize`, `compressedSize`, `offset`, `nbDisk`, and `totalSize`.

## Control Flow

When writing from a file size, the constructor emits size fields only if the file is at least the 32-bit overflow sentinel. When converting LFH extra to CDFH extra, the constructor copies existing size fields and appends offset data if the local-header offset overflows. Parsing first locates the ZIP64 block, validates that its payload size exactly matches the expected overflow fields, then reads fields in the ZIP64-prescribed order selected by the flags.

## State and Persistence Behavior

`Extra` is an in-memory representation of a serialized ZIP extra field. `totalSize` controls whether anything is written. The field persists in local headers and central-directory headers when serialized.

## Dependencies and Integration Points

The header depends on `XrdZipUtils.hh`, `<cstdint>`, and `<sys/types.h>`. It is used by `LFH` and `CDFH` parsing/serialization to handle ZIP64 overflows and by central-directory construction to add offset overflow metadata.

## Risks and Edge Cases

`Find()` advances through variable-length blocks without checking that the next header and data length fit within `end`; malformed extra fields can make it read a short block header or skip beyond the buffer. `FromBuffer()` requires `dataSize == exsize`, but APPNOTE ZIP64 extras may contain fields for only the overflowed values and can coexist with other extra data; the strictness is intentional only if callers compute exactly expected ZIP64 payload sizes. `Serialize()` writes offset only when sizes are absent or positive; combinations involving zero-size ZIP64 files plus offset overflow need careful validation.

## Test Signals

Tests should cover no-overflow files, size overflow, offset overflow, combined size and offset overflow, parsing each flag combination, wrong header ID, wrong data size, truncated extra blocks, multiple extra fields before ZIP64, malformed datasize that exceeds buffer length, and serialization byte-for-byte compatibility with `LFH` and `CDFH` round trips.
