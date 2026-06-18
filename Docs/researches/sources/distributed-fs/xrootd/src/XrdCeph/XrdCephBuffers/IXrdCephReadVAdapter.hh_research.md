# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/IXrdCephReadVAdapter.hh

Purpose: defines the abstraction for converting many readv extents into larger combined read requests.

Important APIs/types/functions: pure virtual `convert(const ExtentHolder &)` returns `std::vector<ExtentHolder>`, where each output holder represents one merged read and contains the original constituent extents.

Control flow: caller translates readv requests into extents, invokes a concrete adapter, then maps combined read data back to original readv segments.

State and persistence: no interface state. Implementations may keep stats, as `XrdCephReadVBasic` does.

Dependencies and integration points: depends on `BufferUtils.hh` for `ExtentHolder`; used by XrdCeph readv-capable file code.

Risks: the interface does not preserve original readv indices, so caller-side ordering/mapping must be reliable. Header includes `<iostream>` with a FIXME, adding unnecessary compile dependency.

Test signals: mock conversion behavior, empty input, unsorted input, overlap/gap cases, and caller mapping back to readv slots.
