# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.cc

Purpose: implements the passthrough `XrdCephReadVNoOp::convert()` adapter for vectored reads. It accepts one `ExtentHolder` containing the caller's requested extents and returns a vector of `ExtentHolder` objects, each holding exactly one original extent. This preserves XRootD `readv` request granularity while allowing the decorator path to use the same `IXrdCephReadVAdapter` interface as coalescing algorithms.

Important APIs and control flow: `convert(const ExtentHolder&)` pulls the immutable `ExtentContainer` from the input, iterates from `begin()` to `end()`, constructs a temporary holder, pushes the current `Extent`, and appends the holder to the output vector. There is no filtering, sorting, merging, or validation. Empty input returns an empty vector.

State and persistence: the implementation is stateless; it only allocates local `std::vector` and `ExtentHolder` instances. Persistence and data transfer are handled later by `XrdCephOssReadVFile`.

Dependencies and integration points: depends on `BufferUtils.hh` for `Extent`, `ExtentContainer`, and `ExtentHolder`, and implements the virtual adapter contract declared in `IXrdCephReadVAdapter.hh`. It is selected by `XrdCephOssReadVFile` when `ceph.readvalgname passthrough` is configured or when an invalid algorithm falls back to passthrough.

Risks and test signals: behavior should be tested with empty, single-extent, and multi-extent holders to ensure output count and order are unchanged. Because later `ReadV` copy-back assumes converted inner extents remain in original request order, any future change that sorts or merges here would need corresponding request-to-buffer mapping tests.
