# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.cc

## Purpose
Implements historical CRC32 plus CRC32C calculation and verification wrappers used throughout XRootD.

## Important APIs and control flow
`CRC32()` computes reflected table-driven CRC-32 with initial and final XORs. `Calc32C(data,count,prevcs)` delegates to `crc32c()` for incremental CRC32C. `Calc32C(data,count,csval)` splits a buffer into `XrdSys::PageSize` pages and writes one CRC32C per full page plus one for a remainder.

`Ver32C()` overloads verify a single checksum, return the first bad page index and computed checksum, fill a boolean per-page success vector, or fill a computed-checksum vector while returning aggregate success. All page-vector variants use page-size segmentation and handle a final partial page.

## State, dependencies, and integration
The file owns the static CRC32 lookup table and depends on `XrdOucCRC32C.hh` for the accelerated CRC32C implementation. CSI page checksum logic and page-read/write utilities depend on these wrappers.

## Risks and test signals
Callers must allocate checksum vectors for the exact number of pages, including a final partial page. The page count uses `int`, so extremely large buffer lengths could overflow on unusual callers. Tests should verify known CRC32 and CRC32C vectors, incremental `prevcs` behavior, page-vector sizing, and mismatch reporting for first and multiple bad pages.
