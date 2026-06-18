<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminQuery.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminQuery.cc

## Purpose
`XrdFrmAdminQuery.cc` implements `frm_admin query` subcommands for path translation, cache-space listing, usage accounting, and transfer queue inspection.

## Important Functions
`QueryPfn()` maps LFNs to local PFNs through `Config.LocalPath()`. `QueryRfn()` maps LFNs to remote names through `Config.RemotePath()`. `QuerySpace()` either lists configured spaces or reports each target file's cache space using `XrdOssPath::getCname()`, optionally recursively through `XrdFrmFiles`. `QueryUsage()` prints `XrdOssSpace` usage buckets and effective usage. `QueryXfrQ()` parses queue type names, optional priority, and optional field names, initializes `XrdFrcProxy` if needed, and lists transfer queue entries.

## Control Flow, State, And Persistence
The query operations are intended to be read-only. `QueryXfrQ()` lazily initializes the transfer queue proxy and may cache failure state in `frmProxz`. Directory expansion uses `VerifyAll()` and `XrdFrmFiles`. Usage queries initialize `XrdOssSpace` and read usage records.

## Dependencies And Integration Points
The file depends on `XrdFrcProxy`, `XrdFrcRequest`, `XrdFrcUtils::MapV2I`, `XrdFrmConfig`, `XrdFrmFiles`, `XrdOssPath`, `XrdOssSpace`, and `XrdOucArgs`. It ties admin-visible variable names to queue record fields.

## Risks And Test Signals
`QuerySpace()` uses prefix matching for `-recursive` with `strncmp(lfn, "-recursive", strlen(lfn))`, so very short prefixes such as `-r` are accepted intentionally or accidentally. Queue field parsing is limited by `XrdFrcRequest::getLast`. Tests should cover no-space configuration, path mapping failures, recursive directory queries, XA/non-XA space names, unknown xfrq queue names, invalid priority, too many variables, and queues absent from `QPath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminQuery.cc -->
