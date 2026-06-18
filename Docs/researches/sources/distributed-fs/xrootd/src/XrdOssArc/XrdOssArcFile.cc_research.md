# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFile.cc

Purpose: implements the archive-aware file object that wraps an underlying OSS file descriptor and optionally redirects reads to a member inside a zip archive. It is the request-time bridge from XRootD open/read/write/fstat calls to archived dataset restoration.

Important APIs/functions: `Open()` classifies the path via `XrdOssArcCompose`, forwards non-archive paths to `ossDF`, stages the backing archive through `XrdOssArcStage::Stage()`, promotes archive-file opens by setting an already-open fd through `Fctl_setFD`, or constructs `XrdOssArcZipFile` for member access. `Close()`, `Fstat()`, `Read()`, and `Write()` dispatch to either the zip member or the underlying OSS file. `getErrMsg()` merges thread-local archive extended errors with lower OSS errors.

Control flow: open first determines whether the path is outside the archive namespace, invalid, the archive itself, or a member. Restore requests run under a child `XrdOssArcStopMon` shared lock so STOP/IDLE drain control can pause restores. Stage returns `EINPROGRESS` as configured wait-policy code `Config.wtpStage`; other errors are negated.

State/dependencies: owns `ossDF` and nullable `zFile`. It depends on `XrdOssArcCompose`, `Config`, `Elog`, `ecMsg`, `XrdSysFD_Open`, and libzip through `XrdOssArcZipFile`. Risks include sign normalization (`Neg()`), promotion fd ownership on `Fctl_setFD`, read-only zip semantics, and member path composition. Test signals: non-archive forwarding, archive-file open, missing member errors with extended messages, stage-in-progress mapping, and write rejection for archive members.
