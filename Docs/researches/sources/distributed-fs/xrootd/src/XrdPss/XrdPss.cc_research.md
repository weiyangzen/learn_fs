<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPss.cc

Purpose: Implements the XRootD Proxy Storage System (PSS) plugin: an `XrdOss` implementation that proxies namespace and file operations to remote XRootD origins through `XrdPosixXrootd`. It also implements proxy file and directory objects, identity mapping hooks, cache-control handling, outgoing proxy URL rewriting, and third-party-copy special cases.

Important APIs/types/functions: `XrdOssGetStorageSystem2()` exports the plugin instance. `XrdPssSys` implements OSS operations including `Init`, `Connect`, `Disc`, `EnvInfo`, `FSctl`, `Lfn2Pfn`, `Mkdir`, `Remdir`, `Rename`, `Stat`, `Stats`, `Truncate`, `Unlink`, `P2DST`, `P2OUT`, `P2URL`, and `Info`. `XrdPssDir` implements `Opendir`, `Readdir`, `StatRet`, `Close`, and error retrieval. `XrdPssFile` implements `Open`, `Close`, sync file I/O, page read/write with checksums, `Fctl`, `Fstat`, `Fsync`, and `Ftruncate`.

Control flow and state: Initialization configures globals, logger/trace, versioning, exported path policy, scheduler/env links, and optional cache FSctl. `P2URL()` is the central path-to-remote URL converter; it applies N2N mapping, origin headers, CGI, generated identities, or outgoing proxy authorization. File open enforces read-only policies, handles `O_DIRECT` as cache I/O hint, checks `only-if-cached`, supports TPC write opens by stashing `tpcPath`, and optionally uses file-cache open handoff. File/directory methods proxy through `XrdPosixXrootd` and store extended error text from `QueryError()`.

Dependencies/integration: Depends on OSS/SFS interfaces, XrdPosix client APIs, XrdPss config/url/util files, XrdNetSecurity, XrdSec entity and sss ID mapping, page read/write utilities, and OFS cache-control plugin interfaces.

Risks and test signals: Risks include mixed errno conventions, read-only/export policy mistakes, unsafe CGI/header URL construction, TPC/reproxy stat fallback behavior, identity mapping lifetime, and cache-control coupling. Tests should run PSS as an OSS plugin against a test origin, covering stat/open/read/write/rename/unlink, exported read-only paths, outgoing proxy authorization, N2N mapping, `only-if-cached`, directory `StatRet`, TPC write-open/fstat/close, and propagated extended errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.cc -->
