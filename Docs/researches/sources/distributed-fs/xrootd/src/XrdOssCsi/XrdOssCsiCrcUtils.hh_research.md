# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.hh

Purpose: provides CRC-32C algebra helpers for page checksum manipulation without rereading full data in every case. It assumes operations are within one `XrdSys::PageSize` page.

Important APIs/functions: `crc32c_combine(crc1, crc2, len2)` returns the CRC of data1 concatenated with data2 by advancing crc1 through zero bytes then XORing crc2. `crc32c_split1(crctot, crc2, len2)` recovers the first segment CRC by reversing through polynomial shifts. `crc32c_split2(crctot, crc1, len2)` recovers the second segment CRC. `crc32c_extendwith_zero(crc, len)` appends zero bytes. Static `g_bz` supplies zero bytes and `CrcPoly` is the reversed iSCSI polynomial.

State/control: all methods are static and assert `len <= PageSize`; they do not allocate or persist state.

Dependencies/integration: used by unaligned page update logic to combine/split partial-page CRCs. Risks include debug-only assertions for oversize lengths, subtle complement/XOR conventions tied to `XrdOucCRC::Calc32C`, and performance comments noting possible optimizations. Tests should use known CRC vectors, random split/combine round trips, zero-length cases, and page-size boundary cases.
