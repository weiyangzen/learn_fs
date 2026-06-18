<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.cc

Purpose: Implements the PSS checksum plugin. It proxies checksum requests to the remote XRootD origin by constructing a PSS URL, issuing `XrdPosixXrootd::QueryChksum()`, and translating the response into `XrdCksData`.

Important APIs/types/functions: `XrdCksInit()` exports a new `XrdPssCks`. Constructor preloads supported algorithms: `adler32`, `crc32`, `md5`, and `crc32c`. `Find()` looks up algorithm metadata. `Get()` builds `cks.type=<name>` CGI, applies `XrdPssSys::P2URL()`, queries checksum and mtime, tokenizes `<name> <value>`, sets `Cks` fields, and returns checksum length. `Init()` can move a supported default algorithm to the front. `Name()` enumerates supported names. `Size()` returns digest length. `Ver()` retrieves and compares checksum data.

Control flow and state: State is a fixed `csTab[8]` and `csLast`. It does not calculate checksums locally; `Calc()` in the header calls `Get()`, and `Set/Del/List` are unsupported or null. `Get()` also uses the caller environment in `Cks.envP` to include identity/CGI handling.

Dependencies/integration: Depends on PSS URL conversion, POSIX checksum query, XrdCks interfaces, tokenization, and trace. Used as a loadable checksum component beside the storage-system plugin.

Risks and test signals: Response parsing is simple and assumes a tokenized checksum response. Tests should cover each supported algorithm, unsupported digest names, remote ENOTSUP/ENOATTR behavior, default algorithm reorder, environment identity propagation, malformed checksum responses, and `Ver()` mismatch and match cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.cc -->
