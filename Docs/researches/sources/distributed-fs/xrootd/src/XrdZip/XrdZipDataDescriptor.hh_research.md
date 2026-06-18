# sources/distributed-fs/xrootd/src/XrdZip/XrdZipDataDescriptor.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipDataDescriptor.hh` defines constants for ZIP data descriptor records. These records appear when CRC and sizes are written after file data rather than in the local header. The source was read as a complete 48-line file.

## Important APIs, Types, and Functions

The exported `struct DataDescriptor` has static `GetSize(bool zip64)`, returning signature plus three 64-bit values for ZIP64 or signature plus three 32-bit values for classic ZIP. It also defines `flag = 1 << 3`, the general-purpose bit indicating a data descriptor, and `sign = 0x08074b50`, the descriptor signature.

## Control Flow

There is no runtime parsing flow in this header. Callers use `HasDataDescriptor()` on CDFH or LFH-related metadata to detect the flag, then use `GetSize()` to compute how many bytes a descriptor should occupy for the ZIP64 mode being processed.

## State and Persistence Behavior

No mutable state is owned. The constants describe serialized archive state that lives in ZIP files.

## Dependencies and Integration Points

The only include is `<cstdint>`. The header is included by `XrdZipCDFH.hh` and likely ZIP reader/writer code that needs descriptor sizing and flag interpretation.

## Risks and Edge Cases

The size model assumes the descriptor includes the optional signature; ZIP variants may omit that signature, so callers must know which form they are handling. `GetSize()` returns `uint8_t`, which is sufficient for the current 16-byte and 28-byte sizes but would be fragile if extended formats were added.

## Test Signals

Tests should assert classic and ZIP64 descriptor sizes, flag matching against CDFH/LFH general bit flags, and reader behavior for archives with descriptor signatures, without descriptor signatures if supported elsewhere, and with ZIP64 size fields.
