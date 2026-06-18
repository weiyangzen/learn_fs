# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVNoOp.hh

Purpose: declares the no-op ReadV adapter in namespace `XrdCephBuffer`. The class gives the Ceph OSS readv decorator a concrete `IXrdCephReadVAdapter` that does not change the request layout, useful for functional testing, instrumentation, and a conservative default path.

Important APIs and types: `class XrdCephReadVNoOp : virtual public IXrdCephReadVAdapter` exposes a trivial constructor/destructor and overrides `std::vector<ExtentHolder> convert(const ExtentHolder&)`. It includes `<vector>`, `<sys/types.h>`, `BufferUtils.hh`, and `IXrdCephReadVAdapter.hh`.

Control flow and integration: the header participates in the strategy selection performed by `XrdCephOssReadVFile`. The adapter's output type matches the decorator's loop over mapped extent groups, so callers can swap between passthrough and `XrdCephReadVBasic` without changing the file wrapper.

State and persistence: no data members are declared. Instances hold no file descriptors, buffers, or Ceph state.

Risks and test signals: the class name and include guard are stable but the file comments contain typos only. Unit tests can instantiate through `IXrdCephReadVAdapter` and assert polymorphic dispatch, output grouping, and zero state sharing across instances.
