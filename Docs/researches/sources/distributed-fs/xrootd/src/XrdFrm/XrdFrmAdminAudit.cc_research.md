<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminAudit.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminAudit.cc

## Purpose
`XrdFrmAdminAudit.cc` implements `frm_admin audit` subcommands for consistency checking and optional repair of namespace metadata, cache-space cross references, and space usage accounting.

## Important Functions
Name audits use `AuditNames()` with `XrdFrmFiles` to detect orphaned sidecar files (`AuditNameNB`), dangling base symlinks (`AuditNameNF`), missing copy-time metadata (`AuditNameNL`), and bad/missing PFN xattrs for extended-attribute layouts (`AuditNameXA`). Space audits use `AuditSpace()` and choose AX or XA logic based on configured space entries. AX checks validate generated PFN symlinks for raw data files. XA checks validate `XrdFrm.Pfn` xattrs and symlinks. Usage audits sum file sizes and compare them with `XrdOssSpace` usage records, optionally adjusting the Admin usage bucket.

## Control Flow, State, And Persistence
The audit flow parses target space/path, walks files, increments `numProb`, `numFix`, `numFiles`, `numBytes`, and `numBLost`, and may prompt before repair unless `-force` is set. Repair actions persist by unlinking orphaned files, creating/replacing symlinks, setting PFN xattrs, setting copy-time xattrs, removing data files, and adjusting usage accounting.

## Dependencies And Integration Points
This file integrates `XrdFrmFiles`, `XrdFrcUtils`, `XrdFrcXAttrPfn`, `XrdOssPath`, `XrdOssSpace`, `XrdOucNSWalk`, and configured space lists from `XrdFrmConfig`. It relies on the admin option state set by `XrdFrmAdmin::Audit()`.

## Risks And Test Signals
Audit repair is destructive and prompt-driven, so noninteractive `-force` behavior needs careful coverage. In `AuditUsage()`, the block that converts byte differences to KB is unconditionally executed because of missing `else` braces, so the display suffix logic is misleading. `AuditSpaceXA()` may count bytes as lost when repair is declined. Tests should create synthetic spaces with missing symlinks, wrong symlinks, missing xattrs, dangling links, stale copy time, absent usage files, and verify both dry-run and fix paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminAudit.cc -->
