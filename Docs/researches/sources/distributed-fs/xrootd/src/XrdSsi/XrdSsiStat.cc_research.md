# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStat.cc

## Purpose
`XrdSsiStat.cc` implements a default OSS stat-info plugin for SSI resources. It lets XRootD stat calls represent provider-managed SSI resources as synthetic regular files and propagate resource add/remove notifications to the SSI provider.

## Important APIs and Functions
The external C functions are `XrdSsiStatInfo` and `XrdOssStatInfoInit2`. `XrdSsiStatInfo` handles both notification calls with null `stat` buffer and stat queries with a real buffer. `XrdOssStatInfoInit2` configures SSI in CMS/stat mode and returns the stat callback.

## Control Flow
For null buffers, the function ignores changes for delegated filesystem paths and otherwise calls `Provider->ResourceRemoved` or `ResourceAdded`. For stat queries, it delegates to the native filesystem when `fsChk` and `FSPath` match. Otherwise it asks the provider for resource status, fills a synthetic regular-file mode for present resources, and marks pending resources with `S_IFBLK` unless `XRDOSS_resonly` is set.

## State and Persistence
The file relies on global provider/config/path state and writes no persistent data. Resource add/remove effects are delegated to the provider implementation.

## Dependencies and Integration Points
It integrates XrdOss stat-info interfaces, `XrdSsiProvider`, `XrdSsiSfsConfig`, `XrdOucPList`, and XRootD version exports. It is loaded by the plugin manager through `XrdOssStatInfoInit2`.

## Risks and Test Signals
Risks include path versus logical filename mismatches, synthetic mode semantics for pending resources, and partial initialization leaving `Provider` null. Tests should cover add/remove notifications, fspath delegation, present/pending/not-present statuses, `XRDOSS_resonly`, init failure on bad config, and versioned symbol loading.
