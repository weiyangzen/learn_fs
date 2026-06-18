# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.hh

Purpose: declares `XrdOssArcFile`, an `XrdOssWrapDF` subclass that presents archived content through the normal XRootD OSS file interface. It preserves the base OSS file contract while adding zip-member reads and archive staging in the implementation.

Important APIs/types: overrides `Open`, `Close`, `Fstat`, `getErrMsg`, `Read(buffer, offset, size)`, and `Write`. The preread overload `Read(off_t,size_t)` is a no-op returning 0. The constructor takes a thread identity and an already-created `XrdOssDF*`; the destructor owns and deletes that file object plus any active `XrdOssArcZipFile`.

Control/state behavior: `ossDF` is always present for forwarding and base-file operations. `zFile` is null for normal or whole-archive opens and non-null when a member inside an archive is open; this boolean state controls dispatch for close, stat, read, and write. Persistence remains in the underlying OSS and archive file; the wrapper holds only per-open process state.

Dependencies/integration: integrates with `XrdOssWrapper.hh` and forward-declares `XrdOssArcZipFile`, `XrdOucEnv`, and `stat`. Risks include ownership clarity for `ossDF`, no-op preread silently dropping cache hints, and write behavior differing by `zFile` state. Tests should cover lifecycle deletion, calls before/after member open, and wrapper behavior under read-only archived members.
