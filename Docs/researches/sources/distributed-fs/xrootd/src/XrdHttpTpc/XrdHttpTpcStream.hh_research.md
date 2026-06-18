# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.hh

Purpose: Declares `TPC::Stream`, a file-handle abstraction with buffering for single-stream-compatible writes during multi-stream TPC pulls.

Important APIs/types/functions: Public API includes `Stat`, `Read`, `Write`, `AvailableBuffers`, `DumpBuffers`, `Finalize`, and `GetErrorMessage`. Nested `Entry` buffers track offset, capacity, size, availability, accepting bytes, write eligibility, and memory shrinkage.

Control flow: The interface is designed for curl callbacks: push reads call `Read`, pull writes call `Write`, and transfer completion calls `Finalize`. The nested `Entry` class only writes when its offset equals the stream offset and, unless forced, when the buffer is full.

State and persistence: Owns an `XrdSfsFile` and heap-allocated reordering buffers. Writes persist through the SFS backend.

Dependencies and integration points: Depends on XRootD SFS and logging. Shared across `State`, single-stream, and multistream TPC paths.

Risks: The constructor sets `m_open_for_write = true` even for streams used for push reads with zero buffers; push code only calls `Read`, but lifecycle semantics are still write-oriented. Raw `Entry*` vector requires destructor/finalize discipline.

Test signals: Buffer lifecycle, no-buffer push stream behavior, and capacity calculation for `streams * m_pipelining_multiplier`.
