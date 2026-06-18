<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPss.hh

Purpose: Declares the PSS plugin classes implementing the server-side OSS proxy interface: `XrdPssDir`, `XrdPssFile`, and `XrdPssSys`. It defines the core class contracts used by `XrdPss.cc`, async I/O, checksum, and config files.

Important APIs/types/functions: `XrdPssDir` derives from `XrdOssDF` and provides directory open/read/close/stat-return behavior plus stored error text. `XrdPssFile` derives from `XrdOssDF` and exposes sync/async file I/O, page read/write, file controls, stats, truncate, sync, and open/close. It stores `tprInfo` for TPC reproxy state, `tpcPath`, client `entity`, and last error info. `XrdPssSys` derives from `XrdOss`, constructs file/dir objects, implements namespace operations, config entrypoints, path-to-URL helpers, feature reporting, and static configuration fields.

Control flow and state: Static fields such as `XPList`, `Police`, `ManList`, `fileOrgn`, `protName`, `hdrData`, `Streams`, `Workers`, `Trace`, `dca*`, `xLfn2Pfn`, `deferID`, and `reProxy` are configured elsewhere and consumed by runtime methods. Per-file state tracks open descriptor, TPC/reproxy metadata, identity, and extended error text.

Dependencies/integration: Uses `XrdOss`, `XrdOucCache`, `XrdOucName2Name`, `XrdOucPList`, `XrdSecEntity`, and POSIX facade types. Async methods are implemented in `XrdPssAio.cc`; checksum plugin in `XrdPssCks.*`.

Risks and test signals: Header-level risks are virtual override compatibility and state ownership. Tests should compile against current OSS ABI, verify destructor closes file/dir resources, exercise `getErrMsg()` clearing semantics, and confirm `Features()` advertises only supported capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.hh -->
