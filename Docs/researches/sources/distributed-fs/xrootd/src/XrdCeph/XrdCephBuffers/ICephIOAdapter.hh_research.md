# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/ICephIOAdapter.hh

Purpose: defines the minimal storage IO interface used by Ceph buffer algorithms.

Important APIs/types/functions: abstract destructor; pure virtual `write(off64_t offset, size_t count)` writes from the associated buffer to Ceph; pure virtual `read(off64_t offset, size_t count)` reads from Ceph into the associated buffer.

Control flow: implementations hide whether IO is synchronous, AIO-backed, striperless, or otherwise. The buffer algorithm only asks to load/flush buffer contents by offset and byte count.

State and persistence: no state in the interface. Implementations are responsible for buffer association and persistent writes.

Dependencies and integration points: includes `IXrdCephBufferData.hh` and is consumed by `IXrdCephBufferAlg`/`XrdCephBufferAlgSimple`.

Risks: the interface does not expose buffer capacity or ownership, so safety relies on implementation/caller discipline. Return convention is POSIX-like `ssize_t` but not documented for partial writes.

Test signals: mock implementations for algorithm tests, partial/error return handling, and replacement of raw adapter with AIO adapter.
