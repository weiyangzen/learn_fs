# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.hh

## Purpose
Declares the concrete file-backed implementation of `XrdOssCsiTagstore`, including the sidecar header marshalling helpers and full-read/full-write utilities.

## Important APIs and types
The constructor takes the logical file name, an owned `XrdOssDF`, and a trace identity. Public overrides implement open/close, flush/fsync, tag I/O, truncation, tracked-size accessors, verification-state mutation, and size resynchronization. `SetTrackedSize()` updates `actualsize_` when needed and writes a new header when the tracked length changes. `SetUnverified()` clears the `csVer` flag and rewrites the header.

`fullread()` repeatedly calls `Read()` until the exact requested byte count is read, returning `-EDOM` on short read. `fullwrite()` loops until all bytes are written. `MarshallAndWriteHeader()` writes magic, tracked length, flags, and a CRC32C over the first 16 header bytes, applying byte swaps when the file byte order differs from the host.

## State, dependencies, and integration
The class owns `fd_`, caches header bytes and endian flags, and stores `trackinglen_`/`actualsize_`. It depends on OSS descriptor APIs, `XrdOucCRC`, `XrdSysPlatform` byte swaps, and the abstract tagstore header.

## Risks and test signals
The destructor closes if still open, so ownership is simple but callers must not retain the moved descriptor. `fullwrite()` assumes zero-byte writes do not occur indefinitely. Tests should cover idempotent close behavior, header CRC calculation, `SetUnverified()` persistence, and exact-byte I/O failure behavior.
