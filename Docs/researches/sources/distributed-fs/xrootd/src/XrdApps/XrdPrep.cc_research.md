# sources/distributed-fs/xrootd/src/XrdApps/XrdPrep.cc

Purpose: implements `xrdprep`, an XrdCl-based command-line client for prepare, cancel, and query requests against an XRootD server.

Important APIs/types/functions: `GetNum` validates numeric options; `Usage` prints supported command modes; `main` parses options and invokes `XrdCl::FileSystem::Prepare` or `Query(QueryCode::Prepare, ...)`. It uses `PrepareFlags` for Evict, Stage, Colocate, Fresh, WriteMode, and Cancel.

Control flow: options are parsed first, then an optional keyword (`cancel`, `query`, `prepare`) determines whether a handle is required or paths are required. The target is converted to `root://host[:port]`. Paths come from remaining arguments plus optional `-f` input file lines. Cancel/query build a newline-separated query buffer; prepare passes the vector directly with priority.

State and persistence: no local persistence. It may read a path list file and exports `XRD_LOGLEVEL` when debug is requested. Server-side prepare state is external to this utility.

Dependencies and integration points: integrates with `XrdCl::FileSystem`, `XrdCl::Buffer`, `XrdOucEnv`, and XRootD server prepare/query protocol. Error messages are normalized from `XRootDStatus`.

Risks: `Target` is a fixed 512-byte buffer populated by `strcpy`/`strcat`; long host arguments can overflow. Total query buffer size is computed from string sizes and newlines, but empty `fList` with query/cancel may produce odd buffer behavior. Option validity is tied to `lastOpt`, so mixed command ordering needs coverage.

Test signals: prepare with paths, prepare from `-f`, cancel/query with handle and optional path filters, invalid numbers, invalid command/option combinations, long host rejection, server error response formatting, and debug environment mapping.
