<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.hh

Purpose: Declares `XrdPosixXrootPath`, the POSIX-layer path translator. It stores virtual mount mappings and exposes helpers for local-path to URL and URL/path to logical-path conversion.

Important APIs/types/functions: `AddProto()` extends the recognized protocol list. `CWD()` records the current working directory for relative path expansion. Static `P2L()` converts supported XRootD URLs to logical/local paths, optionally returning only the path component. `URL()` converts a local path into a URL using configured virtual mount mappings. Internal `xpath` stores linked-list entries with server, source path, and optional replacement path lengths.

Control flow and state: The constructor builds `xplist` from environment configuration; the destructor frees the linked list. `pBase` owns the mutable copy of the environment string used by entries; `cwdPath` tracks relative path context.

Dependencies/integration: Included by `XrdPosixXrootdPath.cc` and consumers that need mapping declarations. Depends only on `<cstring>` in the header to keep it light.

Risks and test signals: Memory ownership is subtle because `xpath` fields point into `pBase`; destructor currently deletes nodes but the research should verify whether `pBase` and `cwdPath` are freed elsewhere or leak intentionally for process lifetime. Tests should include constructor/destructor under repeated initialization, malformed mapping strings, and `URL()` buffer-length failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.hh -->
