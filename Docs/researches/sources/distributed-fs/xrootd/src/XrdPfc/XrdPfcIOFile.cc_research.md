# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.cc

## Purpose
Implements `IOFile`, the standard whole-file proxy-cache adapter. It obtains a shared `File` for the upstream path, validates read bounds, converts sync/async XRootD cache reads into `File` calls, handles page-read checksum calculation, and releases the `File` at detach.

## Important APIs, Types, and Functions
- Constructor calls `Cache::GetInstance().GetFile(GetFilename(), this)`.
- `Fstat()` uses `initialStat()` during construction before `m_file` exists, otherwise delegates to `File::Fstat`.
- `initialStat()` obtains file size from existing local `.cinfo` or upstream `Fstat`.
- `Read()` and async `Read()` allocate `ReadReqRH` wrappers, call `ReadBegin`, wait/callback as needed, then call `ReadEnd`.
- `pgRead()` optionally calculates checksums for forced checksum reads after the data result.
- `ReadV()` and async `ReadV()` mirror the single-read flow for vector reads.
- `ioActive()` and `DetachFinalize()` delegate lifetime and release to `File`.

## Control Flow
Construction attaches to or creates the shared `File`. Each read increments `m_active_read_reqs`, bounds-checks against `FSize()`, sets `m_expected_size`, and delegates to `File`. If `File` returns `-EWOULDBLOCK`, synchronous callers wait on a condition and asynchronous callers return until callback. `ReadEnd` logs short reads/errors, forwards to the external callback, deletes the internal handler, and decrements the active counter.

## State and Persistence Behavior
`IOFile` itself persists nothing. It owns a `File*` reference released through `Cache::ReleaseFile`. Persistent data and `.cinfo` updates are handled by `File`. Error counts and incomplete-read counts are accumulated for detach-time logging.

## Dependencies and Integration Points
Depends on `XrdPfcIOFile.hh`, `Stats`, trace macros, `XrdOss`, `XrdSfs`, `XrdOucEnv`, and `XrdOucPgrwUtils`. It is the concrete adapter used when the cache stores the remote object as one local file.

## Risks and Test Signals
Risks include active read counter balance on all early-return paths, validating `ReadV` chunks against EOF, and `pgRead` lambda lifetime around `csvec`. Tests should cover zero-length/EOF reads, negative offsets, short upstream file size, sync and async callback paths, and `initialStat()` fallback from `.cinfo` to upstream stat.
