# sources/distributed-fs/xrootd/src/XrdCl/XrdClEcHandler.hh

## Purpose
Declares and largely implements the erasure-coded `FilePlugIn` used by XrdCl when redirects identify XRDEC objects. It adapts normal `File` operations onto `XrdEc::Reader` and `XrdEc::StrmWriter`.

## Important APIs, Types, And Functions
Important types include `FreeSpace`, `ServerSpaceInfo`, `EcPgReadResponseHandler`, `EcHandler`, `EcPlugInFactory`, and `GetEcHandler`. `EcHandler` implements plugin methods for `Open`, `Close`, `Stat`, `Read`, `PgRead`, `Write`, `PgWrite`, and `IsOpen`. Private helpers load placement for writes or reads, synthesize `StatInfo` responses, and schedule async responses through `ResponseJob`.

## Control Flow
`Open` rejects unsupported write/update combinations, loads placement when needed, and constructs a stream writer for new write-only files or a reader for read-only files. `Close` closes the active writer or reader; writer close can issue an opaque commit query containing object id, close marker, size, and optional checksum. `Stat` delegates to metadata file stat unless `nomtfile` is enabled, in which case it serves cached or live reader/writer sizes. `Read` and `Write` delegate to the XrdEc reader/writer; writes must be sequential at `curroff`. `PgRead` wraps normal reads and converts `ChunkInfo` into `PageInfo` with CRC32C per-page checksums. `PgWrite` validates supplied CRC32C digests before writing.

## State And Persistence
`EcHandler` stores redirect URL, a metadata `FileSystem`, `ObjCfg`, optional writer/reader, current write offset, optional checksum helper, and stat cache. Persistent server-side effects are erasure-coded data writes, opaque close commits, xattrs used to find current stripe versions, and placement selected from server locate/space data.

## Dependencies And Integration Points
Depends on the plugin interface, utilities, checksum helper, response jobs, `XrdEc::Reader`, `XrdEc::StrmWriter`, CRC/page utilities, `FileSystem`, `LocationInfo`, and `DefaultEnv::GetPostMaster()`. `EcPlugInFactory` is used by plugin registration to create EC file handlers for configured erasure-coding layouts.

## Risks
Most methods are inline in the header, increasing rebuild and ABI exposure. `PgWrite` casts `buffer` to `const char *` and then deletes it when checksums are present, which is dangerous because callers may own the buffer and it may not have been allocated with `new[]`. `EcPgReadResponseHandler` drops responses silently if `ChunkInfo` extraction fails. Async lambdas capture `this`; callback ordering must not outlive the handler. Placement loading allocates `FileSystem` per server and queries xattrs synchronously. Unsupported operations are only partially covered by the plugin surface.

## Test Signals
High-value tests cover read and write open modes, unsupported flag combinations, sequential write enforcement, close commit query content, checksum-on-close, `PgRead` checksum generation, `PgWrite` checksum mismatch behavior, `nomtfile` stat caching, stripe-version xattr selection, and callback lifetime under async close/read failures.
