# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOssFile.hh

Purpose: declares the base Ceph file descriptor object implementing `XrdOssDF`.

Important APIs and types: `XrdCephOssFile : virtual public XrdOssDF` exposes open/close, sync and async reads/writes, `ReadV`, `ReadRaw`, `Fstat`, `Fsync`, `Ftruncate`, and `getFileDescriptor()`. Protected members are `int m_fd` and `XrdCephOss *m_cephOss`.

Control flow and integration: this class is the common base for decorators. `XrdCephOssReadVFile` and `XrdCephOssBufferedFile` inherit virtually and wrap an owned `XrdCephOssFile*` while also using inherited `m_fd` for adapter creation and logging.

State and persistence: tracks a synthetic fd allocated by the POSIX shim. No object data is stored in the class.

Dependencies: includes `XrdOss.hh` and `XrdCephOss.hh`.

Risks and test signals: inheritance and ownership tests should ensure wrappers do not obscure the fd or double-close. API tests should verify direct `ReadV` versus decorated `ReadV` behavior under configuration.
