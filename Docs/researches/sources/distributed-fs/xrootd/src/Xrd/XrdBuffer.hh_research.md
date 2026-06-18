<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.hh

Purpose: declares `XrdBuffer`, the memory wrapper handed to protocol/runtime code, and `XrdBuffManager`, the normal buffer pool.

Important APIs/types/functions: `XrdBuffer::{buff,bsize}`, constructor/destructor, private `bindex`/`next`, `XrdBuffManager::{Init,Obtain,Recalc,Release,MaxSize,Reshape,Set,Stats}`, constants `XRD_BUCKETS` and `XRD_BUSHIFT`, and private bucket/counter/state members.

Control flow: header exposes the pool contract: initialize background reshaping, obtain a buffer of at least requested size, calculate actual allocation size, release a buffer, reshape/retune memory limits, and emit stats. `XrdBuffer` frees owned memory in its destructor.

State and persistence behavior: buffers own heap memory, not persisted data. `buff` and `bsize` are public for fast I/O use, while `bindex` and freelist linkage are private to the buffer managers.

Dependencies: standard allocation/unistd/sys/types and `XrdSysPthread` for `XrdSysCondVar`. `XrdBuffManager` friends `XrdBuffer`; `XrdBuffXL` is a friend for large-buffer handling.

Integration points: central allocator used by `XrdProtocol_Config::BPool`, stats, protocol I/O, and buffer tuning directives. `XRD_BUCKETS`/`XRD_BUSHIFT` define the normal pool range and drive `XrdBuffXL` thresholds.

Risks: public mutable `buff` and `bsize` are performance-oriented but allow accidental misuse; callers must not free `buff` directly or change `bsize` inconsistently. The manager destructor exists but comments say it is never deleted, so cleanup assumptions are daemon-oriented.

Test signals: compile tests for consumers; ownership tests that destructor frees memory exactly once; pool API tests; integration tests through protocol reads/writes and stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdBuffer.hh -->
