# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephOss.cc

Purpose: implements the XRootD OSS plugin entry point and storage-system object for Ceph-backed files. It translates XRootD OSS operations into `ceph_posix_*` calls and optionally wraps file objects with readv and buffering decorators.

Important APIs: `XrdOssGetStorageSystem()` initializes logging, parses default Ceph parameters, installs the POSIX log callback, and returns `XrdCephOss`. `Configure()` parses directives such as `ceph.nbconnections`, `ceph.namelib`, `ceph.usedefaultpreadalg`, `ceph.usedefaultreadvalg`, `ceph.aiowaitthresh`, `ceph.usebuffer`, `ceph.buffersize`, `ceph.buffermaxpersimul`, `ceph.usereadv`, `ceph.readvalgname`, `ceph.bufferiomode`, and `ceph.reportingpools`. File-system methods implement `Stat`, `StatFS`, `StatLS`, `StatVS`, `Truncate`, `Unlink`, and directory/file factories; unsupported mutations like `Create`, `Rename`, and `Chmod` return `-ENOTSUP`, while directory create/remove intentionally return success for POSIX-assuming clients.

Control flow: configuration sets global POSIX knobs and instance decorator options. `Stat()` handles fake root stats, pool-name location for space reporting, and object stat through `ceph_posix_stat()`. `StatLS()` validates configured reporting pools, queries used bytes via pool stats, reads a `total_space` xattr from `<pool>:__spaceinfo__`, and formats OSS spaceinfo fields. `newFile()` creates a base `XrdCephOssFile`, optionally wraps it in `XrdCephOssReadVFile`, then optionally in `XrdCephOssBufferedFile`.

State and persistence: instance fields retain configuration only. Persistent storage state is in Ceph; process-wide connection pools and file descriptors live in `XrdCephPosix.cc`. The destructor calls `ceph_posix_disconnect_all()`.

Dependencies and integration points: integrates with XRootD plugin versioning, `XrdOucStream`, name-to-name loaders, `XrdSysError`, `XrdCephPosix`, and decorator classes. `m_translateFileName()` uses global `g_namelib`.

Risks and test signals: config parsing needs coverage for invalid numbers, missing values, and decorator order. `StatLS()` depends on substring matching in `m_configPoolnames` and a Ceph xattr convention. `ceph.usereadv` logs `m_configBufferEnable` rather than the readv setting, which is a diagnostic risk. Tests should cover root stat, pool stat, object stat, spaceinfo formatting, and all file factory combinations.
