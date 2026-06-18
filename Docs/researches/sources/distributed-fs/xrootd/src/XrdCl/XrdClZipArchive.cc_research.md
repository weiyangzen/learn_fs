# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.cc

## Purpose

This file implements `XrdCl::ZipArchive`, a remote ZIP archive helper built on XRootD file operations. It can open an archive, parse the central directory including ZIP64 metadata, read entries by name with local-buffer or remote-read paths, support deflated-entry reads through `ZipCache`, list archive contents as `DirectoryList`, append new files, update metadata, serialize a new central directory, and close/commit changes.

It is an asynchronous pipeline-oriented bridge between XRootD remote file I/O and ZIP structure parsers from `XrdZip`.

## Important APIs, types, and functions

- Template `ReadFromImpl<RSP>()` is shared by `ReadFrom()` (`ChunkInfo`) and `PgReadFrom()` (`PageInfo`). It validates archive state, finds the central directory entry, computes the actual local-file-data offset, handles supported compression methods, serves from local archive buffer when possible, queues deflate reads through `ZipCache`, or issues remote `RdWithRsp<RSP>()` pipelines.
- Constructor initializes `archive`, sizes/flags (`archsize`, `cdexists`, `updated`, `cdoff`, `orgcdsz`, `orgcdcnt`), open parser stage (`None`), and checkpoint flag (`ckpinit`).
- `OpenOnly()` opens a remote ZIP file without parsing the central directory, sets `archsize` and `openstage = NotParsed`, and calls the user handler.
- `OpenArchive()` opens and parses the archive. It reads the trailing EOCD search window, locates EOCD, optionally follows ZIP64 EOCD locator/record, reads central directory records, validates offsets and compressed-size totals, stores original central-directory bytes, and marks `openstage = Done`.
- `OpenFile()` opens an existing archive member for read or prepares a new `LFH` for append when `OpenFlags::New` is used.
- `GetCD()` serializes the current central directory plus EOCD/ZIP64 EOCD/locator as needed.
- `SetCD()` installs a central directory from an external buffer for archives previously opened with `OpenOnly()`.
- `CloseArchive()` writes updated local file headers and central directory at `cdoff`, optionally wraps operations in checkpoint commit, closes the underlying file, and clears state on success.
- `ReadFrom()` and `PgReadFrom()` delegate to the shared template.
- `List()` builds a `DirectoryList` with per-entry `StatInfo` derived from archive stat info and each entry's uncompressed size.
- `WriteImpl()` appends data, writing an `LFH` before the first data chunk when needed, uses `ChkptWrtV` if overwriting an existing central directory, updates `archsize`/`cdoff`, adds `CDFH`/`cdmap`/`newfiles` records, and initializes checkpoints when necessary.
- `UpdateMetadata()` updates CRC32 in both the central-directory entry and stored new-file LFH.
- `AppendFile()` creates an LFH and writes a whole new entry in one call.

## Control flow

Opening a parsed archive is a staged async pipeline. After `Open()`, empty files immediately become `Done` with no central directory. Non-empty files read up to `EOCD::maxCommentLength + EOCD::eocdBaseSize + ZIP64_EOCDL::zip64EocdlSize` bytes from the tail. The read continuation loops over `openstage`: parse EOCD, detect whole-archive-in-buffer shortcut, detect ZIP64 locator, read ZIP64 EOCD when needed, read central directory records, copy original CD bytes, parse `CDFH` records, validate offsets/aggregate compressed size, and finish. `Pipeline::Repeat()` is used when the same read stage must be reissued with new offset/size/buffer.

Reading an entry derives its data offset indirectly: it finds the next central-directory record or CD offset, subtracts compressed size and optional data-descriptor size, then adds the requested relative offset. For stored entries, data is either copied from `me.buffer` or read remotely. For deflated entries, requests are queued in a per-file `ZipCache`; if the whole archive is buffered the compressed bytes are fed to the cache immediately, otherwise the code reads remote compressed bytes and queues them as cache responses.

Appending is append-only relative to `cdoff`. The first write for a new file writes local-file-header plus user data; subsequent writes omit the LFH. The original central directory may be overwritten, so checkpointed writes are used when `archsize > cdoff`. Closing an updated archive writes any modified LFHs for overwritten CRC metadata, writes the serialized central directory, optionally commits the checkpoint, closes, clears state on success, and reports through the response handler.

## State and persistence behavior

`ZipArchive` persists no metadata outside the remote archive file, but it mutates the remote file through XRootD writes. Important in-memory state includes:

- `archive`, the underlying `XrdCl::File`.
- `archsize`, current archive size as tracked by open/write operations.
- `cdexists`, `updated`, `ckpinit`, and `openstage` state flags.
- `cdoff`, `orgcdsz`, and `orgcdcnt`, representing central-directory location and original CD shape.
- `eocd`, `zip64eocd`, `cdvec`, `cdmap`, and `orgcdbuf`, representing parsed and original ZIP metadata.
- `buffer`, which may hold either a tail/CD read buffer or the entire archive for local serving.
- `openfn` and `lfh`, representing the currently open archive entry/new local header.
- `newfiles`, tracking appended files and LFHs that may need CRC/header rewrites.
- `zipcache`, one deflate cache per compressed entry.

Remote persistence occurs in `WriteImpl()` and `CloseArchive()`: entry bytes are appended before the central directory, and close writes final metadata. Checkpoints are used to make central-directory overwrite safer when appending to an archive with an existing CD.

## Dependencies and integration points

The file depends on `XrdClFileOperations.hh` and `XrdClCheckpointOperation.hh` pipeline combinators (`Open`, `Read`, `RdWithRsp`, `Write`, `WriteV`, `VectorWrite`, `ChkptWrtV`, `Checkpoint`, `Close`, `Final`, `Async`), `XrdClZipArchive.hh`, logging/default env/constants/utils, `XrdZip` structures (`EOCD`, `CDFH`, `LFH`, `DataDescriptor`, `ZIP64_EOCD`, `ZIP64_EOCDL`), `ZipCache`, `DirectoryList`, `StatInfo`, and POSIX `sys/stat.h`.

Friend declarations in the header allow EC components (`XrdEc::StrmWriter`, `Reader`, `OpenOnlyImpl`) and tests to access internal state. The archive reports async completion through `ResponseHandler` and packages read responses as `ChunkInfo` or `PageInfo`.

## Risks and edge cases

- ZIP offset math is delicate. The file data offset is inferred from the next record and compressed size rather than by reading the LFH extra/name lengths directly; unusual layouts, prepended data, or malformed central directories can expose edge cases.
- Deflated remote reads use `relativeOffset` to derive compressed read offsets, but compressed and uncompressed offsets are not equivalent. `ZipCache` may compensate by needing sequential compressed data, but sparse reads into deflated files are a key risk area.
- Only stored (`compressionMethod == 0`) and deflated (`Z_DEFLATED`) entries are supported; all other methods return `errNotSupported`.
- `memcpy(usrbuff, me.buffer.get() + offset, size)` assumes `buffer` covers the requested absolute offset. That is true only when the whole archive was buffered; parser stages reset `buffer` after CD-only reads.
- `SetCD()` parses external metadata only when `openstage == NotParsed` and performs less explicit corruption handling than `OpenArchive()`.
- `WriteImpl()` advances `archsize` and `cdoff` before the async write completes. A later write failure sets callback error state but callers must treat the archive object carefully after failures.
- `CloseArchive()` has code using `uint32_t lfhlen = lfh->lfhSize` inside a loop over `newfiles` where `nf.lfh` is the intended object; if `lfh` is null at close, this would be unsafe. The serialized buffer uses `nf.lfh`, so the length source deserves review.
- Asynchronous lambdas capture `this` and references such as `&cache`/`&me`; callers must keep the `ZipArchive` object alive until callbacks finish.
- Central-directory validation checks offsets and aggregate compressed size but does not fully validate every local header or data descriptor.

## Test signals

Tests should cover empty archives, normal EOCD parsing, ZIP64 EOCD locator/record parsing, max-comment EOCD search, malformed signatures/offsets/sizes, whole-archive buffered reads, CD-only reads, stored file remote reads, deflated full and partial reads through `ZipCache`, reads past EOF, unsupported compression, directory listing metadata, append-new-file flow, duplicate append rejection, CRC metadata update, close with and without checkpoint, close failure state, `OpenOnly()` plus `SetCD()`, and object lifetime under async callbacks. Regression tests should specifically inspect `CloseArchive()` LFH rewrite length handling and compressed sparse-read behavior.
