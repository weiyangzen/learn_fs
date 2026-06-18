## sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.cc

### Purpose
This file implements asynchronous reads from XrdEc striped/erasure-coded objects. It opens data archives, reads metadata or xattrs, maps logical reads to block/stripe zip entries, verifies checksums, reconstructs missing stripes through `RedundancyProvider`, supports scalar reads and a host-batched vector-read path, and closes archives.

### Important APIs, Types, and Functions
- `OpenOnlyImpl` is a private XrdCl zip operation that opens an archive without parsing its central directory immediately.
- Internal `block_t` caches all stripes for one block and tracks stripe state: `Empty`, `Loading`, `Valid`, `Missing`, and `Recovering`.
- `block_t::read`, `read_callback`, `error_correction`, `get_stripes`, `carryout`, and `fail_missing` implement per-block cache reads and recovery.
- `Reader::Open`, `Read`, `VectorRead`, and `Close` implement public operations.
- `Reader::Read(blknb, strpnb, buffer, cb)` reads one zip entry, verifies its CRC, and schedules callback.
- `ReadMetadata`, `ReadSize`, `ParseMetadata`, `AddMissing`, and `IsMissing` build the URL map and missing-stripe set.
- `MissingVectorRead` and `ErrorCorrected` coordinate vector-read fallback reconstruction.

### Control Flow
Open constructs a `ZipArchive` per placement URL. In normal metadata mode it opens data archives with `OpenOnly` and reads one replicated metadata file, then installs central directories into the zip archives and builds `urlmap`. In `nomtfile` mode it opens archives normally and reads `xrdec.filesize` from xattrs. The open operation requires at least `nbdata` data archives.

Scalar `Read` trims reads past EOF in `nomtfile` mode, splits the requested range by block and data stripe, obtains or creates a cached `block_t`, and issues `block_t::read` for each stripe. The shared read context aggregates byte counts and final status before scheduling the user's handler.

`block_t::read` starts an async stripe read for empty stripes, queues pending user reads while loading or recovering, serves valid cached data immediately, and triggers error correction when a requested stripe is missing. Recovery is possible if missing plus recovering stripes do not exceed parity and enough valid stripes are available; otherwise it loads additional empty stripes until `nbdata` are available and marks missing stripes recovering. When recovery succeeds, pending reads for recovered stripes are carried out.

Vector read groups requested stripe zip offsets by host/archive, issues XrdCl vector reads per host in chunks of at most 1024, verifies each requested stripe checksum, and falls back to `MissingVectorRead` for failed or corrupt stripes. The final handler waits on `waitMissing`, copies data from reconstructed block buffers into either a global buffer or per-chunk buffers, and returns success only if all segments are valid.

### State and Persistence
Reader state includes data archive map, central-directory metadata buffers during open, `urlmap`, missing set, a one-block scalar-read cache, file size, archive index map, and vector-read missing coordination state. It does not write persistent data. Persistent inputs are remote zip archives, optional `.mt` metadata files, and `xrdec.filesize` xattrs.

### Dependencies and Integration Points
The implementation depends on XrdCl async pipelines, `ZipArchive`, file and zip operations, XrdZip record parsers, XrdEc utilities, thread pool, singleton config, and redundancy provider. XrdCl EC handler owns `Reader` and forwards File read/vector-read operations to it.

### Risks and Edge Cases
The scalar cache only stores one block, so interleaved reads across blocks can evict useful state. `Read` only trims EOF in `nomtfile` mode; metadata mode appears to rely on missing zip entries to signal EOF. In checksum verification, one branch checks `st` instead of the result variable from `GetCRC32`, which may miss CRC lookup failures. `IsMissing` returns true for `nomtfile` when `fntoblk(fn) <= lstblk`, which looks counterintuitive and deserves tests. Vector read allocates `StatInfo* info` and may use it without guarding failed `Stat`; it also ignores per-chunk statuses in `VectorReadInfo` and treats whole-host status as representative. `missingChunksVectorRead` wait can deadlock if a fallback callback is never invoked. The vector final copy does not trim against `filesize` the same way scalar read does.

### Test Signals
Tests should include open with metadata and no-metadata modes, missing metadata replicas, central directory parsing, scalar reads crossing stripe and block boundaries, checksum mismatch recovery, unrecoverable missing count, EOF behavior, close of open archives, vector read with many chunks, failed host fallback, per-stripe CRC failure, global versus per-chunk buffers, and concurrency between scalar/vector reads.
