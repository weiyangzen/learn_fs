# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.hh

## Purpose
Declares the low-level CRC32C functions used by `XrdOucCRC`.

## Important APIs
`crc32c(uint32_t crc, void const *buf, size_t len)` computes CRC32C over a byte sequence, allowing chunked continuation with the previous return value and requiring the first call use `crc == 0`. It may use Intel hardware instructions when available. `crc32c_sw()` provides the same calculation but forces the software implementation.

## State, dependencies, and integration
The header depends only on `<cstddef>` and `<cstdint>`. It is the narrow C-style API boundary between generic XRootD checksum code and the optimized implementation.

## Risks and test signals
The comments are part of the contract for incremental use; callers passing a nonzero initial CRC that was not produced by a prior call will get a valid continuation but not a standalone checksum. Tests should compare `crc32c()` and `crc32c_sw()` on the same data and verify chunked results equal one-shot results.
