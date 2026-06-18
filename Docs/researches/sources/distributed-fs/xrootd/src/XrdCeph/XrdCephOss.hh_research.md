# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.hh

Purpose: declares the `XrdCephOss` class, the main XRootD OSS implementation for Ceph storage. It documents path parameter precedence for user, pool, and layout defaults.

Important APIs and types: `XrdCephOss : public XrdOss` overrides the storage-system lifecycle and file-system surface: `Configure`, `Init`, `Stat`, `StatFS`, `StatLS`, `StatVS`, `Truncate`, `Unlink`, `Mkdir`, `Remdir`, `newDir`, and `newFile`. Public flags `m_useDefaultPreadAlg` and `m_useDefaultReadvAlg` steer base file read behavior. Private fields hold buffer/readv feature toggles, buffer size/mode, max simultaneous buffers, readv algorithm name, and reporting pool list.

Control flow and integration: the header defines the configuration state consumed in `XrdCephOss.cc` and by wrappers such as `XrdCephOssBufferedFile` and `XrdCephOssFile`. It is included by most Ceph OSS classes to access the parent object and algorithm flags.

State and persistence: only runtime configuration is stored here; Ceph connections, fd maps, and object metadata are external.

Dependencies: includes XRootD `XrdOss.hh` and `XrdSysError.hh`, plus `<string>`.

Risks and test signals: public mutable algorithm flags make behavior dependent on configuration and object sharing. Tests should verify default values, config overrides, and that buffered/readv decorators observe the configured flags.
