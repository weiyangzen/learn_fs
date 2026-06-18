<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.hh

Purpose: Declares the page read/write checksum and layout utility API.

APIs and control flow: Public static methods compute checksums, count checksum slots, verify data with resumable `dataInfo`, and calculate receive/send `Layout` values. `Layout` records buffer offset, data length, socket length, first/last segment lengths, and failure reason.

State and persistence: The class has no instance state. Callers provide buffers, checksum arrays, `dataInfo`, and `Layout` structs.

Dependencies and integration: Includes `<cstdint>`, `<vector>`, and POSIX `off_t`. The implementation binds it to protocol page-size and CRC semantics.

Risks and test signals: Callers must size checksum buffers according to `csNum()` and honor `eWhy` when layout functions return zero. Tests should validate header/API assumptions for pgRead/pgWrite clients and servers, especially iovec construction from `fLen` and `lLen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPgrwUtils.hh -->
