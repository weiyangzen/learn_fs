# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTypes.hh

## Purpose
Defines shared simple types for the proxy file cache, currently checksum policy flags and checksum-vector storage.

## Important APIs, Types, and Functions
- `enum CkSumCheck_e`: checksum states `CSChk_Unknown`, `CSChk_None`, `CSChk_Cache`, `CSChk_Net`, `CSChk_Both`, and configuration-only `CSChk_TLS`.
- `typedef std::vector<uint32_t> vCkSum_t`: checksum vector used by page read/write paths.

## Control Flow
No functions or control flow. The enum is consumed by configuration, `Info`, and `File` to decide whether to request network checksums, write cache checksums, or downgrade metadata state.

## State and Persistence Behavior
`CkSumCheck_e` values are persisted inside `Info::Status` bitfields in `.cinfo`; `vCkSum_t` is transient per block/read.

## Dependencies and Integration Points
Depends on `<cstdint>` and `<vector>`. Included by `Info`, `File`, and checksum-related cache code.

## Risks and Test Signals
Risks include treating `CSChk_TLS` as a persistent state even though the comment says it is configuration-only, and bitfield width compatibility with negative `CSChk_Unknown`. Tests should cover enum serialization through `Info` and configuration downgrade logic.
