# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.cc

Purpose: implements the base `XrdOssDF` file object for Ceph. It is the innermost file layer and maps XRootD file operations to the `ceph_posix_*` shim.

Important APIs: `Open()` calls `ceph_posix_open()` and stores the returned synthetic fd. `Close()` calls `ceph_posix_close()`. Synchronous `Read()` uses either striper `ceph_posix_pread()` or direct-object `ceph_posix_nonstriper_pread()` based on `m_useDefaultPreadAlg`, with fallback to striper on sparse or unsupported cases. `ReadV()` similarly chooses `ceph_striper_readv()` or `ceph_nonstriper_readv()`. AIO methods call `ceph_aio_read()` and `ceph_aio_write()` with callbacks that set `aiop->Result` and invoke XRootD completion. `Fstat`, `Write`, `Fsync`, and `Ftruncate` delegate to the POSIX shim.

Control flow: fallback paths log a warning when direct object reads fail with `-ENOENT` or `-ENOTSUP` and striper reads then succeed. `Read(off_t,size_t)` is a stub returning `XrdOssOK`, matching XRootD's optional read-without-buffer signature.

State and persistence: stores only the current synthetic fd and parent OSS pointer. Persistent object content is controlled by `XrdCephPosix.cc`.

Dependencies and integration: used directly or wrapped by readv/buffer decorators. Depends on `XrdSfsAio`, `XrdCephPosix`, and parent configuration flags.

Risks and test signals: tests should cover read algorithm fallback, AIO callback results, bad fd handling through POSIX functions, write access errors, and decorator inheritance of `m_fd`. The unbuffered `Read(off_t,size_t)` stub should be verified against XRootD expectations.
