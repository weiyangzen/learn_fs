# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephXAttr.cc

Purpose: implements the XRootD `XrdSysXAttr` plugin for Ceph objects using the same POSIX shim defaults and path syntax as the OSS plugin.

Important APIs: `XrdSysGetXAttrObject()` sets the log prefix, logger, and default Ceph parameters, then returns `XrdCephXAttr`. `Del`, `Get`, `List`, and `Set` dispatch to fd-based POSIX xattr calls when an fd is supplied and path-based calls otherwise. `Free()` delegates list cleanup to `ceph_posix_freexattrlist()`.

Control flow: path-based methods catch syntax exceptions from path parsing and return `-EINVAL`. `Set()` ignores the `isNew` creation-only flag and always passes flags `0` to Ceph.

State and persistence: the class has no members. Persistent checksum or metadata values are Ceph xattrs on objects.

Dependencies and integration: uses XRootD plugin versioning, `XrdSysError`, `XrdOucTrace`, and `XrdCephPosix` xattr functions. It can share global Ceph defaults with the OSS plugin when loaded in the same process.

Risks and test signals: tests should cover fd 0 handling (`List()` uses `fd > 0` while `Get`/`Set` use `fd >= 0`), ignored `isNew`, binary xattr values, path syntax errors, and list/free memory correctness through the POSIX shim.
