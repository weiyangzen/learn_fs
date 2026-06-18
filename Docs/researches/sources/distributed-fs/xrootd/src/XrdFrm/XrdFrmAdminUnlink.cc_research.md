<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminUnlink.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminUnlink.cc

## Purpose
`XrdFrmAdminUnlink.cc` implements recursive and non-recursive removal for `frm_admin rm`, including OSS-backed deletion, namespace walking, cache manager notifications, and CNS notification events.

## Important Functions
`Unlink()` maps an LFN to PFN, stats it, dispatches files to `UnlinkFile()`, directories to `UnlinkDir()`, and recursive directories through `XrdOucNSWalk`. `UnlinkDir(const char*, const char*)` handles single-directory deletion or all-files deletion with confirmation. `UnlinkDir(NSEnt*&, NSEnt*&)` removes files immediately and defers directories for later removal. `UnlinkFile()` chooses raw `unlink()` for special path types and `Config.ossFS->Unlink()` for normal files, then notifies CMS and CNS.

## Control Flow, State, And Persistence
Deletion is persistent and safety-gated by `Opt.All`, `Opt.Recurse`, and `Opt.Force`. Recursive removal walks children first, remembers directories, then removes them after file deletion succeeds. Counters `numFiles`, `numDirs`, and `numProb` track results. CNS notifications are sent through `XrdFrmCns::Rm()` and `Rmd()`.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig`, `XrdFrmCns`, `XrdNetCmsNotify`, `XrdOss`, `XrdOssPath`, `XrdOucNSWalk`, and POSIX stat/unlink. It is called by `XrdFrmAdmin::Remove()`.

## Risks And Test Signals
This is destructive code, so tests should use isolated namespaces. Non-recursive directory removal special-cases a lone `DIR_LOCK`; the comparison uses `Config.lockFN` against `NSE.nP->Path`, which may be a full path rather than a basename depending on `NSWalk` behavior. CNS `Rmd()` is sometimes passed PFN and sometimes LFN with `islfn=1`; translation should be verified. Tests should cover file deletion, empty directory deletion, directory with lock file, directory with subdirectories without `-recursive`, recursive confirmation abort, echo output, CMS notification, CNS notification, and OSS failure returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminUnlink.cc -->
