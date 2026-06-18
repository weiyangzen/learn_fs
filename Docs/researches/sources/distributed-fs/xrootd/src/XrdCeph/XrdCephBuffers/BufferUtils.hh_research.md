# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.hh

Purpose: declares common helpers used by the Ceph buffering layer.

Important APIs/types/functions: debug macro `BUFLOG`; `Timer_ns`; `Extent`; `ExtentContainer`; `ExtentHolder`. `Extent` exposes range predicates and subset extraction. `ExtentHolder` exposes aggregate range, contained/missing byte accounting, sorting, and copies of extents.

Control flow: classes are simple value/RAII utilities. `BUFLOG` builds a string under a mutex and writes to `std::clog` when `CEPHBUFDEBUG` is defined.

State and persistence: no persistent state beyond the debug mutex declared externally. `ExtentHolder` caches `m_begin` and `m_end` as extents are pushed.

Dependencies and integration points: included by all buffer/readv concrete classes and interfaces. It is part of the XrdCeph module, not a public installed API in this file.

Risks: `CEPHBUFDEBUG` is hard-defined to `1`, meaning debug logging is always compiled and can be noisy/expensive. Comments mention future xrootd logging integration. The range math uses `off_t + size_t` conversions, so overflow should be considered for very large offsets.

Test signals: compilation in debug/non-debug variant if macro changes, thread-safe logging smoke test, and all extent/holder behavior used by readv merging.
