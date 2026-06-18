## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.cc

Purpose: implements transfer workers for stage/fetch, copy-in, copy-out, migration, and migration-with-purge. It wraps externally configured copy commands, fail-file throttling, local/remote path translation, copy-time persistence, notifications, and monitoring.

Important APIs and control flow: `Init()` initializes cluster IDs, the transfer queue, and worker threads split between in/out/any queues. `Start()` loops on `XrdFrmXfrQueue::Get()`, dispatching to `Fetch()` for inbound queues or `Throw()` for outbound/migration queues, then calls `Done()`. `Fetch()` resolves a remote source, checks fail files, skips existing local files, optionally creates `.anew` placeholders, runs the command, finalizes with `FetchDone()`, removes temp files on failure, and notifies CMS. `Throw()` resolves a remote destination, checks resident source and fail files, validates migration eligibility with `ThrowOK()`, runs the outgoing command, verifies no source modification, and either purges local data or calls `ThrowDone()`. `SetupCmd()` performs macro substitution for command arguments.

State and persistence: fail files persist retry state; `.anew`, `.lock`, and copy xattrs persist transfer/migration metadata. `pTab` caches created remote directories for `cmdMDP`. Successful operations update CNS/CMS and monitor streams.

Dependencies and integration: depends on `XrdFrmXfrQueue`, `XrdFrmXfrJob`, `XrdFrcRequest`, `XrdOucProg`, `XrdOss`, xattr helpers, `CID`, `XrdFrmCns`, `XrdFrmMonitor`, and global configuration.

Risks and test signals: high risk centers on external command exit semantics, path buffer mutation (`PFN[pfnEnd]` sidecar suffixes), fail-file directory length limits, and verifying files modified during copy. Tests should cover URL/non-URL command selection, `cmdAlloc`, `cmdRME`, `cmdMDP`, nofile fail mtimes, old/new copy-time persistence, purge-on-success, monitor payloads, and notification return codes.
