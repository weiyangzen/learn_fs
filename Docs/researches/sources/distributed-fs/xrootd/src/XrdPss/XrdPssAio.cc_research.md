<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAio.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssAio.cc

Purpose: Implements asynchronous file and page I/O methods for `XrdPssFile`. It adapts server-side `XrdSfsAio` requests to the async callback APIs exposed by `XrdPosixXrootd` and `XrdPosixExtra`.

Important APIs/types/functions: `Fsync(XrdSfsAio*)` queues async fsync. `Read(XrdSfsAio*)` and `Write(XrdSfsAio*)` queue async pread/pwrite. `pgRead(XrdSfsAio*, opts)` queues page-read and optionally forces checksum retrieval. `pgWrite(XrdSfsAio*, opts)` optionally verifies caller checksums, calculates or copies CRC vectors, then queues page-write through `XrdPosixExtra::pgWrite()`.

Control flow and state: Each async method allocates an `XrdPssAioCB` bound to the `XrdSfsAio`, read/write direction, and page-read/write mode. For page writes, checksum handling is performed synchronously before queuing so invalid checksums return `-EDOM` immediately. Completion is handled later by the callback object, which writes result fields and invokes done callbacks.

Dependencies/integration: Depends on `XrdPosixXrootd` async methods, `XrdPosixExtra` page I/O, `XrdOucPgrwUtils`, `XrdSfsAio`, and `XrdPssAioCB`.

Risks and test signals: The methods do not check `fd < 0` before queueing, so caller/open-state assumptions are important. Async tests should cover successful read/write/fsync, failed descriptor paths, pgRead checksum copyback, pgWrite verify failure, generated checksum return to caller, callback recycling, and close while operations are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAio.cc -->
