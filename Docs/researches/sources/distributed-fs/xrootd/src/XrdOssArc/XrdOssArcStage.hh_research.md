# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.hh

Purpose: declares the scheduled job used for archive staging. The class is intentionally small: it stores the active archive path and exposes static helpers used by the file wrapper before archive access.

Important APIs/types: `enum MssRC { isBad=-1, isFalse=0, isTrue=1 }` represents MSS online checks. `static isOnline(const char*)` wraps the configured MSS command. `static Stage(const char* path, const char* mssPath)` starts or observes staging for an archive and returns 0, `EINPROGRESS`, or an errno. `DoIt()` runs the scheduled stage operation. Private `Reset()` changes the active path and removes completed entries from the active set; `StageError()` records an error code for later callers.

Control/state behavior: object instances are scheduled jobs and self-delete in the implementation. `arcvPath` is valid only while the path is present in the global active set; this comment is important because queued work reuses path pointers from copied `ActInfo` records.

Dependencies/integration: depends on `XrdJob` and C string helpers. It is called by `XrdOssArcFile::Open()` before archive or member access. Test signals should verify idempotent return for already-active paths, status after failed staging, and safe object lifetime through pending queue transitions.
