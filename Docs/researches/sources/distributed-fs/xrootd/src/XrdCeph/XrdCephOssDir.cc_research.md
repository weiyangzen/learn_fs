# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.cc

Purpose: implements the directory side of the Ceph OSS plugin. Because Ceph object pools do not have true POSIX directories, this class delegates to the POSIX shim's object iterator abstraction.

Important APIs: the constructor stores the parent `XrdCephOss*` and initializes `m_dirp`. `Opendir()` calls `ceph_posix_opendir(&env, path)` and maps null to `-errno`, catching parameter syntax exceptions as `-EINVAL`. `Readdir()` calls `ceph_posix_readdir()`. `Close()` calls `ceph_posix_closedir()` and returns success.

Control flow and integration: `XrdCephOss::newDir()` constructs this class. The POSIX layer only accepts root-like paths and returns object names derived from striper object suffixes.

State and persistence: `m_dirp` holds a cast `DirIterator` pointer allocated in `XrdCephPosix.cc`. No directory entries are persisted by this class.

Risks and test signals: `Close()` does not guard null `m_dirp`; tests should cover failed `Opendir()` followed by cleanup behavior. Directory listing tests should verify object suffix filtering and buffer truncation through the POSIX shim.
