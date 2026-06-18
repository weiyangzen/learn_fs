## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.cc

Purpose: implements `XrdFrmFileset` and `XrdFrmFiles`, the namespace scanner and fileset assembler used by purge and migration. It walks configured storage paths, groups a base file with migration sidecars such as `.lock`, `.pin`, `.fail`, and `.pfn`, and exposes refreshed stat/xattr state to higher-level policy code.

Important APIs and control flow: `XrdFrmFiles::Get()` drains already-built filesets, otherwise calls `XrdOucNSWalk::Index()` for a directory and `Process()` to hash entries by base filename. `Process()` handles compressed directory storage, recognizes suffixes through `XrdOssPath::pathType()`, ignores/removes some old-mode artifacts in new-run mode, and emits one fileset per logical base name. `XrdFrmFileset::Screen()` rejects orphaned sidecars or missing copy-time evidence, optionally deleting orphans when `Config.Fix` is set. `Refresh()` re-stats base and lock files, checks file locks, and refreshes pin/copy xattrs.

State and persistence: file state is read from filesystem stat records, old-mode lock-file mtimes, and new-mode `XrdFrcXAttrCpy`/`XrdFrcXAttrPin` xattrs. `BadFiles` suppresses repeated error messages until purged by callers.

Dependencies and integration: used by `XrdFrmMigrate::Scan()` and `XrdFrmPurge::Scan()`. It depends on global `XrdFrm::Config`, `XrdOucNSWalk`, `XrdOssPath`, xattr helpers, and `XrdFrc::Say` logging.

Risks and test signals: `Mkfn()` is explicitly non-reentrant when directory compression is enabled; callers must not share one fileset across threads. Path construction assumes enough shared directory buffer for filenames. Tests should cover old/new run modes, orphan sidecar removal, compressed directory mode, lock contention, xattr absence, symlink `Link` paths, and recursive scan error propagation via `rc`.
