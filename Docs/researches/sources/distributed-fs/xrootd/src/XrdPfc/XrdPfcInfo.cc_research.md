# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.cc

## Purpose
Implements `.cinfo` metadata serialization for cached files. It records block size, file size, creation time, checksum policy/state, synced block bitmap, prefetch bitmap, and compacted access records, with compatibility readers for older metadata versions.

## Important APIs, Types, and Functions
- `Info::Write()` writes version 4 metadata: version, `Store`, store CRC32C, synced bitmap, access records, and combined bitmap/access CRC32C.
- `Info::Read()` reads v4 or dispatches to `ReadV2`/`ReadV3`, validates checksums, copies synced bitmap to written bitmap, and recomputes completion.
- `ResizeBits()` allocates and zeroes written/synced/prefetch bitmaps based on file size and buffer size.
- `SetBufferSizeFileSizeAndCreationTime()` initializes new metadata.
- `ResetCkSumCache()`/`ResetCkSumNet()` downgrade checksum state and set no-checksum timestamp.
- `CompactifyAccessRecords()` merges access records when exceeding `s_maxNumAccess`.
- `WriteIOStatAttach`, `WriteIOStat`, `WriteIOStatDetach`, and `WriteIOStatSingle` update access history.
- `ReadV2()` and `ReadV3()` read legacy MD5-protected formats and translate access records.

## Control Flow
New metadata initialization sets sizes, allocates bitmaps, and records creation time. Writes compact access records, update astat size, and emit checksummed sections. Reads first load the version; v4 validates `Store` checksum before allocating bitmaps, then validates synced bitmap plus access records. Legacy readers load size/bitmap/MD5, then tolerate truncated or corrupt trailing access records by reading until failure and skipping invalid entries.

## State and Persistence Behavior
The persistent `.cinfo` v4 format intentionally stores the synced bitmap, not merely the written bitmap, so restart does not trust blocks written after an incomplete fsync. `m_buff_written` is runtime download state, `m_buff_synced` is durable state, and optional `m_buff_prefetch` stores prefetch-source stats. Access records are persisted and compacted to a configured maximum.

## Dependencies and Integration Points
Depends on `XrdOssDF` positional IO, `XrdOucCRC32C`, `XrdCksCalcmd5`, `XrdPfcStats`, `Cache` configuration for checksum tests, and trace macros. `File`, `IOFileBlock`, purge state, print tooling, and resource monitoring consume `Info`.

## Risks and Test Signals
Risks include unchecked allocation failures, division by zero if buffer size is invalid, metadata endianness/ABI assumptions from raw struct serialization, and compatibility with partially written `.cinfo`. Tests should cover v4 checksum mismatch, v2/v3 migration, access compaction boundaries, incomplete fsync recovery, checksum downgrade timestamps, and empty/tiny file edge cases.
