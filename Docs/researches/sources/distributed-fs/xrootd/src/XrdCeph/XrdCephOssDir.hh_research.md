# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssDir.hh

Purpose: declares `XrdCephOssDir`, the `XrdOssDF` directory object returned by the Ceph OSS plugin.

Important APIs: constructor accepts `XrdCephOss*`; virtual methods are `Opendir`, `Readdir`, and `Close`. The class stores `DIR *m_dirp` and a parent pointer.

Control flow and integration: the header allows `XrdCephOss.cc` to instantiate directory handles while hiding the Ceph iterator details behind the standard OSS directory API.

State and persistence: state is a transient directory iterator pointer. Object listing state comes from librados `NObjectIterator` in the POSIX layer.

Risks and test signals: tests should verify that `Opendir("/")` and non-root paths map to the expected success/error behavior, and that `Close()` releases the iterator.
