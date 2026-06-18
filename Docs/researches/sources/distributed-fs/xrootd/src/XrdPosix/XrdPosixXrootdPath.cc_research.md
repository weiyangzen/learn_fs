<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.cc

Purpose: Implements path and URL translation for the POSIX layer. It maps local paths to XRootD URLs using `XROOTD_VMP`, converts supported XRootD URLs back to local/translated logical paths for cache/name2name use, and allows extra protocol prefixes.

Important APIs/types/functions: Constructor parses `XROOTD_VMP` tokens of the form `server:path[=replacement]` into linked `xpath` entries. `AddProto()` registers additional protocol prefixes in the fixed-size `protoTab`. `CWD()` stores a normalized current working directory for relative `./` paths. `P2L()` recognizes supported XRootD protocols, strips URL prefix/path/cgi, optionally appends `?src=` and CGI for N2N translators, invokes `theN2N->pfn2lfn()`, and returns either the original path or allocated replacement. `URL()` maps a path to `root://server/path`, applying CWD and optional replacement path.

Control flow and state: Per-instance state is `xplist`, `pBase`, `cwdPath`, and `cwdPlen`. Global state in `XrdPosixGlobals` includes `protoTab`, `theN2N`, `oidsOK`, `p2lSRC`, and `p2lSGI`. `P2L()` returns allocated memory through `relP` only when translation happened; callers must free it.

Dependencies/integration: Used by POSIX config/path handling and cache mutation paths in `XrdPosixXrootd.cc`. Integrates with `XrdOucName2Name`, `XrdOucTokenizer`, and trace macros.

Risks and test signals: Risks include fixed protocol-table capacity, malformed `XROOTD_VMP` tokens, buffer limits, URL CGI preservation, and object-id/double-slash semantics. Tests should cover protocol registration, VMP replacement, relative CWD paths, N2N success/failure errno propagation, CGI handling, object-id allowance, and auth-obfuscated debug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.cc -->
