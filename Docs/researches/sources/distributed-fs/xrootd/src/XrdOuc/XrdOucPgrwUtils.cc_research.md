<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.cc

Purpose: Implements checksum and iovec layout helpers for XRootD page read/write protocol messages.

APIs and control flow: `csCalc()` computes CRC32C checksums over page-sized segments, handling unaligned leading fragments. The vector overload sizes and fills a checksum vector. `csNum()` computes checksum count and optionally first/last segment lengths. `csVer()` verifies data against checksums, updates `dataInfo` past verified or failed ranges, and reports bad offset/count. `recvLayout()` validates socket bytes containing interleaved checksums and computes data/socket lengths and first/last data fragment lengths. `sendLayout()` computes the corresponding layout for outbound data.

State and persistence: All functions are stateless except for mutating caller-provided `dataInfo` and `Layout`. No persistence occurs.

Dependencies and integration: Uses `XProtocol` page size constants and `XrdOucCRC` CRC32C helpers. It sits directly in pgRead/pgWrite network and filesystem I/O paths.

Risks and test signals: Off-by-one and alignment errors can corrupt data. Tests should cover aligned and unaligned offsets, short final pages, invalid buffer sizes, zero lengths, checksum mismatch resume behavior, and maximum integer-sized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.cc -->
