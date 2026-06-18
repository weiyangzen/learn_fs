# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.hh

## Purpose
Declares `Info`, the in-memory representation and serializer for proxy-cache metadata files. It defines the persistent `Store` structure, access-stat records, block-state bitmaps, checksum-state helpers, and public metadata operations.

## Important APIs, Types, and Functions
- `Status`: bitfield storing `CkSumCheck_e` state.
- `AStat`: one access record with attach/detach time, IO count, duration, merge count, and hit/miss/bypass bytes.
- `Store`: persistent header with buffer size, file size, creation/no-checksum time, access count, status, and access vector size.
- Bit APIs: `SetBitWritten`, `TestBitWritten`, `SetBitSynced`, `SetAllBitsSynced`, `SetBitPrefetch`, `TestBitPrefetch`.
- Size/completion APIs: `ResizeBits`, `GetNBlocks`, `IsComplete`, `UpdateDownloadCompleteStatus`, `GetExpectedDataFileSize`.
- Serialization APIs: `Read`, `Write`, checksum calculators, v2/v3 readers.
- Access APIs: `WriteIOStat*`, `CompactifyAccessRecords`, `GetLatestDetachTime`, `GetLastAccessStats`.

## Control Flow
`File` uses the class by initializing sizes, marking blocks written/synced as data is downloaded and fsynced, then writing metadata. Restart paths read metadata, validate checksums, reconstruct written state from synced state, and use completion/expected-size helpers to decide whether local data is usable.

## State and Persistence Behavior
`Store`, synced bitmap, and access records are persisted. Written and prefetch buffers are runtime state, although prefetch bits can be used while the `Info` object lives. Static `s_infoExtension` defines `.cinfo`, and `s_maxNumAccess` bounds access history persistence.

## Dependencies and Integration Points
Depends on `XrdPfcTypes.hh`, `Stats`, `XrdOssDF`, `XrdCksCalc`, and `XrdSysTrace`. It is consumed by `File`, `IOFile`, `IOFileBlock`, `FsTraversal`, purge, and print tooling.

## Risks and Test Signals
Risk areas are inline bit operations relying on assertions, off-by-one in block count and expected data size, and raw serialized struct compatibility. Tests should exercise bitmaps around byte boundaries, last partial block, complete/incomplete transitions, and access record merge behavior.
