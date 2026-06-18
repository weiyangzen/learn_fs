# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/CephIOAdapterAIORaw.hh

Purpose: declares the AIO-backed raw Ceph adapter and its blocking AIO helper object.

Important APIs/types/functions: `CephBufSfsAio` derives from `XrdSfsAio` and overrides `doneRead`, `doneWrite`, `Recycle`; exposes mutex, unique lock, condition variable, and `isDone`. `CephIOAdapterAIORaw` implements `ICephIOAdapter::read/write`.

Control flow: callers use the same synchronous adapter interface as raw IO; the implementation uses callbacks and condition variables internally.

State and persistence: adapter state is non-owned buffer pointer, fd, timing/byte counters. `CephBufSfsAio` owns synchronization state for one operation.

Dependencies and integration points: includes XrdSfs AIO interface, buffer interfaces, and utilities. It is interchangeable with `CephIOAdapterRaw` at the algorithm layer.

Risks: synchronization fields are public and unusual; `unique_lock` as a member invites ownership misuse. Buffer pointer ownership is explicitly not taken, so construction order and lifetime matter.

Test signals: header ABI compatibility with XrdSfsAio, construction/destruction, read/write override dispatch through `ICephIOAdapter`, and lifetime tests where buffer outlives adapter.
