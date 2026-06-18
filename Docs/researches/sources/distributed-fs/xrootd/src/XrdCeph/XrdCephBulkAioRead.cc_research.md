# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBulkAioRead.cc

Purpose: implements `bulkAioRead`, a helper that converts one logical file read into parallel librados object reads for non-striper access. It is used by `ceph_posix_nonstriper_pread()` and `ceph_nonstriper_readv()` to read striped object suffixes directly when files have a single stripe.

Important APIs: the constructor stores `librados::IoCtx*`, a variadic log wrapper, and `CephFileRef*`. `read()` decomposes a file offset and request length into object-local chunks using `file_ref->objectSize`; `addRequest()` creates per-object `ObjectReadOperation` entries and `ReadOpData` buffers; `submit_and_wait_for_complete()` issues `aio_operate()` for each object and waits for all completions; `get_results()` copies returned `bufferlist` data into client buffers and clears internal vectors/maps.

Control flow: callers enqueue one or more logical reads, submit all collected operations, then call `get_results()`. Object names are generated as `<file_ref->name>.<16 hex object index>`, matching the RADOS striper object suffix convention. The implementation returns early on allocation failures, suffix formatting overflow, librados return values, or internal length checks.

State and persistence: `operations` groups operations by object index and `buffers` owns output buffer metadata until completion. It does not persist file metadata; it relies on `CephFileRef` for object layout and file name. `clear()` is called by the destructor and after successful result collection.

Dependencies and integration: depends on librados C++ APIs, `CephFileRef` from `XrdCephPosix.hh`, and error constants. It deliberately bypasses `RadosStriper` reads for performance on single-stripe files.

Risks and test signals: request splitting across object boundaries, zero-length reads, sparse object `ENOENT`, allocation failure, and partial result copy should be covered. `submit_and_wait_for_complete()` does not cancel remaining AIOs after a failure, so error-path lifetime and completion cleanup are important integration tests.
