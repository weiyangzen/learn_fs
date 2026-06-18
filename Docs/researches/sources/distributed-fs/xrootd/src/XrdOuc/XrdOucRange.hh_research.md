# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRange.hh

Purpose: defines `XrdOucRange`, a small generic range descriptor used to pass file offsets, byte counts, and caller-defined metadata through XRootD storage and file-system interfaces. The header also standardizes `XrdOucRangeList` as `std::vector<XrdOucRange>` for pre-read and vectored I/O APIs.

Important APIs, types, and functions: `XrdOucRange` exposes public `offset`, `size`, and `info` fields plus a value constructor. `XrdOucRangeList` is the only named container alias. The destructor is virtual, allowing derived range records to be passed through base pointers if a component extends the record.

Control flow: there is no algorithmic flow; callers construct range objects, populate fields directly or through the constructor, and pass vectors to consumers. The `info` field is deliberately opaque so sfs/ofs/oss layers can attach local semantics without another type.

State and persistence: all state is caller-owned in memory. No locking, allocation beyond the vector container, or persistence is involved.

Dependencies and integration points: depends only on `<vector>`. The comment identifies integration with sfs, ofs, and oss pre-read paths where file offsets and lengths must be batched across module boundaries.

Risks and test signals: `size` is an `int`, so very large single ranges need splitting by callers. `info` is untyped and can become ambiguous between producers and consumers. Useful tests are compile-time API compatibility, vector handoff through pre-read paths, and bounds handling for zero or negative sizes at consuming layers.
