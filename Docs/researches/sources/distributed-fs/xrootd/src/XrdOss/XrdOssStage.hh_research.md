# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.hh

Purpose: declares `XrdOssStage_Req`, the queue node used by OSS real-time staging.

Important APIs/types/functions: flag macros `XRDOSS_REQ_FAIL`, `XRDOSS_REQ_ENOF`, and `XRDOSS_REQ_ACTV`; list members `fullList` and `pendList`; path hash, path, size, flags, signal/ETA time, and priority fields; static `StageMutex`, `ReadyRequest`, and sentinel `StageQ`.

Control flow: the constructor initializes both intrusive list nodes to point at the request and duplicates the path when provided. The sentinel constructor form points list nodes at another object. The destructor frees the path and removes the node from both intrusive lists, so deleting a request also unlinks it from queue state.

State and persistence behavior: request state is in memory only. It records whether a stage is pending, active, failed, or failed because the remote file is absent, plus byte size and ETA/failure hold time.

Dependencies: `XrdOucDLlist`, `XrdSysError`, `XrdSysPthread`, C time/stat types.

Integration points: consumed by `XrdOssStage.cc` worker and lookup predicates. The intrusive list behavior makes ownership and deletion the queue-management mechanism.

Risks: destructor side effects require all deletion to occur under `StageMutex`; copying is not disabled; a failed allocation in `strdup` leaves `path` null; default size is a large estimate that influences ETA before remote size is known.

Test signals: list insertion/removal invariants, destructor unlinking, duplicate lookup, active/failure flag transitions, and worker deletion under lock.
