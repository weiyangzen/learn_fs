# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.hh

## Purpose
`XrdClZipArchive.hh` declares `XrdCl::ZipArchive`, the client-side facade for treating an ordinary XRootD `File` as a ZIP archive. It supports opening and parsing an existing archive, listing central-directory contents, opening an archive member for read or append, reading member data, writing new entries, updating metadata, closing the archive, and exposing member stat and CRC information.

## Important APIs and Types
The public API centers on `OpenArchive`, `OpenFile`, `Read`, `PgRead`, `ReadFrom`, `PgReadFrom`, `Write`, `UpdateMetadata`, `AppendFile`, `Stat`, `GetCRC32`, `GetOffset`, `CloseArchive`, `CloseFile`, and `List`. `Read` and `PgRead` are convenience wrappers over the current `openfn`; `ReadFrom` and `PgReadFrom` take an explicit archive member name. `Stat` uses central-directory metadata plus the underlying archive file's `StatInfo`. `GetOffset` computes the member payload offset from central-directory ordering, ZIP64 size metadata, and any data descriptor.

The key private state includes the underlying `File archive`, archive size, central-directory existence/update flags, EOCD and ZIP64 EOCD records, `cdvec` and `cdmap`, original central-directory buffer/offset/count, current open stage, currently open member name, per-file inflate caches, the pending LFH for appended files, checkpoint state, and `newfiles` entries that may require LFH overwrite on close. `OpenStages` models the parser state from no data through EOCD, ZIP64 locator, ZIP64 EOCD, central-directory records, done, error, and open-without-parse.

## Control Flow
Opening moves through `OpenArchive` and parser stages until the central directory is available. Reads validate that the archive and member are open, then eventually map logical member offsets to underlying archive reads; compressed members are mediated through `ZipCache`. Append/write flow creates a new LFH, writes file bytes, remembers new central-directory state, and finalizes via `CloseArchive`. `Schedule`, `PkgRsp`, and `Free` adapt status/response objects to XrdCl's callback job manager.

## State and Persistence
Persistent archive changes are deferred in memory until writes and close operations update LFH/CD structures in the underlying archive file. `Clear` resets parser and central-directory state without owning external storage. `newfiles` tracks append entries whose local headers may need rewriting after final CRC/size metadata is known.

## Dependencies and Integration Points
This header binds `XrdCl::File`, `ResponseHandler`, `ResponseJob`, `JobManager`, `DefaultEnv`, and `PostMaster` to low-level `XrdZip` record types (`EOCD`, `CDFH`, `ZIP64_EOCD`, `LFH`). Friends in `XrdEc` and tests access internals. `ZipOperations.hh` wraps this API into the operation pipeline.

## Risks and Test Signals
Offset math in `GetOffset` is sensitive to ZIP64 sentinel values, data descriptors, and central-directory order. Only stored and deflated members are accepted. Inline callback scheduling transfers ownership of heap status/response objects, so tests should cover null handlers, failed stats, missing central-directory entries, ZIP64 archives, compressed sequential reads, unsupported compression methods, append close rewriting, and repeated open/clear cycles.
