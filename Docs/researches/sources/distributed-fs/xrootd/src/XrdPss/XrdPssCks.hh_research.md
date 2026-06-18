<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.hh

Purpose: Declares `XrdPssCks`, an `XrdCks` implementation that exposes checksum operations for proxied files. It supports remote retrieval and verification but does not support mutating checksum metadata.

Important APIs/types/functions: `Calc()` delegates to `Get()`. `Get()`, `Init()`, `Name()`, `Size()`, and `Ver()` are implemented in the `.cc`. `Del()` and `Set()` return `-ENOTSUP`; `List()` returns null; `Config()` accepts config lines as a no-op success. Internal `csInfo` stores a checksum algorithm name and byte length.

Control flow and state: `csTab` is a fixed-size table of up to eight supported algorithms, with `csLast` marking the last populated entry. The class uses inherited `XrdCks` error destination for config messages.

Dependencies/integration: Includes `XrdCks` and `XrdCksData`; forward-declares `XrdSysError`. The implementation integrates with PSS URL mapping and `XrdPosixXrootd`.

Risks and test signals: Header behavior signals that local calculation and metadata mutation are intentionally unsupported despite `Calc()` name. Tests should ensure callers handle `-ENOTSUP`, algorithm size reporting is stable, default selection from `Init()` works, and verification does not mutate caller data unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.hh -->
