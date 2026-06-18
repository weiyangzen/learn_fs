# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstore.hh

## Purpose
Declares the abstract sidecar checksum tag storage interface used by CSI page checksum code. Implementations persist per-page CRC32C tags and metadata about the amount of data covered by those tags.

## Important APIs and types
`XrdOssCsiTagstore` exposes lifecycle methods `Open()` and `Close()`, durability methods `Flush()` and `Fsync()`, bulk tag I/O methods `WriteTags()` and `ReadTags()`, size/status accessors `GetTrackedTagSize()`, `GetTrackedDataSize()`, and `IsVerified()`, plus state mutators `SetTrackedSize()`, `SetUnverified()`, `ResetSizes()`, and `Truncate()`. The `csVer` flag marks a tag file whose checksums are considered verified.

## State, dependencies, and integration
The interface depends on `XrdOss.hh` for `XrdOucEnv`, `XrdOssDF`, and OSS error conventions. It stores no state itself; concrete implementations such as `XrdOssCsiTagstoreFile` hold the file descriptor and header.

## Risks and test signals
The contract uses negative errno-style returns and `ssize_t` tag counts, so callers must distinguish bytes from tag entries. Implementations must keep tracked data length, tag file length, and verified/unverified state consistent across open, write, truncate, and close. Tests should use a mock tagstore for page logic and an on-disk implementation test for endian, truncation, and header integrity.
