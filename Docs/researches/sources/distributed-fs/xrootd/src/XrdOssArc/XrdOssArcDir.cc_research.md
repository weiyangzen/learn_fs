# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.cc

Purpose: implements archive-aware directory wrapper behavior, mainly opening archive zip files as directory-like objects while delegating non-archive paths.

Important APIs/types/functions: destructor, `Close`, `getErrMsg`, and `Opendir`.

Control flow: `Opendir()` creates a minimal `XrdOssArcCompose` with no env. Non-archive paths are forwarded to the underlying `ossDF`. Backup paths reject directory listing with `EPERM`. Archive paths compose the archive zip path, open it with `XrdSysFD_Open`, then promote the fd into the wrapped DF via `Fctl_setFD` to bypass normal name translation. `Close()` closes and deletes `zFile` if present, otherwise closes `ossDF`.

State and persistence behavior: owns the underlying `XrdOssDF*` and optional `XrdOssArcZipFile*`. It opens local/tape-buffer archive files read-only and does not modify archive contents.

Dependencies: `XrdOssArcCompose`, `XrdOssArcZipFile`, `XrdOucEnv`, `XrdOucECMsg`, `XrdSysFD`, `XrdSysError`, and the wrapper base class.

Integration points: returned by `XrdOssArc::newDir`. It lets archive paths participate in OSS directory operations by adapting an opened archive file descriptor into the existing OSS DF abstraction.

Risks: return for backup listing is positive `EPERM` instead of `-EPERM`, unlike surrounding methods; `zFile` is never assigned in this file, suggesting companion behavior or dead state; promoting an fd depends on underlying `Fctl_setFD` support; path buffer diagnostics can log uninitialized `arcPath` on composition failure.

Test signals: non-archive pass-through, backup `Opendir` denial sign convention, archive path open failure, successful fd promotion, close after promotion, error-message composition with underlying OSS messages.
