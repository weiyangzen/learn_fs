<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcRequest.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcRequest.hh

## Purpose
`XrdFrcRequest.hh` defines the fixed-size request record used by FRM/FRC transfer queues. It is a data-only ABI structure: queue code stores logical file names, request IDs, notification targets, checksum metadata, timestamps, queue linkage offsets, operation options, URL offsets, original operation code, and priority in one contiguous object.

## Important APIs, Types, And Constants
The public `XrdFrcRequest` class exposes only fields and constants. `LFN`, `User`, `ID`, `Notify`, `iName`, and `csValue` are fixed arrays intended for direct queue serialization. `This` and `Next` are integer offsets into queue storage rather than pointers, which makes the queue persistent or mmap-friendly. `Options` is a bitset using `msgFail`, `msgSucc`, `makeRW`, `Migrate`, `Purge`, and `Register`. `csType` uses the `csNone`, SHA, Adler32, MD5, and CRC constants. `Item` enumerates printable queue fields consumed by queue listing code, especially `XrdFrcUtils::MapV2I()` and `XrdFrcProxy::List()`. Queue constants map operation classes to queue IDs: stage, migrate, get, put, nil, and `outQ` as a mask.

## Control Flow And State
There is no executable control flow. The important behavior is layout stability: other queue components can read and write records by offset and decode fields by agreed constants. `LFO` and `Opaque` preserve parsing offsets within `LFN` when the logical name is a URL or includes opaque query text. `addTOD` records enqueue time and `Prty` controls priority queue placement up to `maxPrty`.

## Dependencies And Integration Points
The header has no includes and intentionally avoids dependencies. It is integrated by `XrdFrcUtils` for operation-to-queue mapping and variable-name mapping, by `XrdFrcProxy` for queue operations, and by `frm_admin query xfrq` for field selection. Since all fields are public, producer and consumer code must agree on null termination and bounds.

## Risks And Test Signals
The fixed arrays protect against dynamic allocation but create truncation and overflow risks if callers use unchecked string copies. Persistent queue compatibility depends on field ordering and sizes; changes require migration tests over existing queue files. Tests should verify operation code mappings, field listing names, URL offset semantics, priority bounds, checksum type handling, and binary layout assumptions such as `sizeof(XrdFrcRequest)` and offsets if queue files are persisted across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcRequest.hh -->
