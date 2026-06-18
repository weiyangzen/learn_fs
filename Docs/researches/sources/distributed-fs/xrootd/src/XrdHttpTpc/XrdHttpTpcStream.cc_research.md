# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.cc

Purpose: Implements the file stream abstraction used by HTTP TPC to read local files for push and write local files for pull, including out-of-order buffering for multistream downloads.

Important APIs/types/functions: Destructor deletes buffers and closes the file handle. `Finalize` deletes buffers, closes the file, and verifies all reordering buffers are available. `Stat`, `Read`, `Write`, `WriteImpl`, and `DumpBuffers` wrap SFS operations and diagnostics.

Control flow: Writes reject closed streams and prior offsets. In-order MB-aligned or forced writes go directly to SFS. Otherwise, data is accepted into `Entry` buffers, and the stream repeatedly tries to flush buffers whose offset matches `m_offset`. Forced zero-size writes flush partial buffers at EOF. Memory for unused buffers may shrink under low occupancy.

State and persistence: Holds `unique_ptr<XrdSfsFile>`, current write offset, open-for-write flag, available-buffer count, vector of `Entry*`, and last error message. Durable persistence is the SFS file being written/closed.

Dependencies and integration points: Depends on `XrdSfsFile`, `XrdSysError`, and the TPC `State` callbacks. Supports HDFS/RADOS constraints described in comments by presenting sequential/aligned writes.

Risks: `Finalize` deletes all buffer entries before checking `m_avail_count == m_buffers.size()`, so outstanding-buffer detection relies on the saved count rather than inspecting entries. Destructor closes the file even after `Finalize` already closed it, unless SFS close is idempotent. Buffer management is pointer-based and sensitive to partial accept/write logic.

Test signals: Ordered writes, out-of-order range writes, forced final flush, buffer exhaustion, short write and SFS error propagation, finalize with outstanding buffers, destructor after finalize, and push `Read` path.
