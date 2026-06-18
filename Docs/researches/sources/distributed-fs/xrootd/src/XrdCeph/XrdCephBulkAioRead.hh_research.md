# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.hh

Purpose: declares the non-striper bulk asynchronous read helper and the small RAII wrappers it uses around librados read operations and completions.

Important APIs and types: `CmplPtr` wraps `librados::AioCompletion*`, with `use()`, `wait_for_complete()`, `get_return_value()`, and destructor release behavior. `ReadOp` pairs an `ObjectReadOperation` with a completion. `ReadOpData` stores the caller's output pointer, a `ceph::bufferlist`, and librados return code. `bulkAioRead` exposes `read()`, `submit_and_wait_for_complete()`, `get_results()`, and `clear()`, while `addRequest()` is private.

Control flow and integration: callers declare file-coordinate reads, then explicitly submit/wait and harvest results. The class is not a general POSIX file object; it is a batch builder used inside `XrdCephPosix.cc` to implement faster `pread` and `readv` against direct RADOS object names.

State and persistence: stores mutable maps/vectors of pending operations and temporary bufferlists. It borrows the `IoCtx`, log function, and `CephFileRef`; those must outlive the helper.

Dependencies: uses `<map>`, `<vector>`, `<memory>`, librados, and `XrdCephPosix.hh`. The log callback uses the same function pointer shape as the POSIX shim.

Risks and test signals: lifetime tests should verify completion release, no use after `CephFileRef` deletion, repeated `read()` calls before submit, and post-`get_results()` reuse. Boundary tests should use offsets at object edges and multi-object reads.
