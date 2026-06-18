# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.cc

Purpose: implements an `XrdSfsDirectory` adapter for SSI. SSI itself does not provide directory listing semantics; this file delegates directory operations to the underlying configured filesystem only when the path is allowed by the global filesystem path list.

Important APIs and control flow: `open()` rejects reuse when `dirP` is already set, checks `fsChk && FSPath.Find(dir_path)`, allocates a real directory via `theFS->newDir()`, copies error context, and delegates `open()`. If the path is not filesystem-backed it returns `ENOTSUP`. `nextEntry()`, `close()`, `autoStat()`, and `FName()` all forward to `dirP` when open and otherwise set `EBADF`.

State and persistence: state is a single delegated `XrdSfsDirectory *dirP` owned by the wrapper. No persistent storage is modified. Global dependencies are `XrdSsi::theFS`, `XrdSsi::FSPath`, and `XrdSsi::fsChk`.

Integration points: used by the SSI SFS layer to support directory operations only for passthrough filesystem paths. This keeps service-request paths from accidentally exposing directory semantics. Risks include returning `ENOTSUP` for all non-FS paths, lifecycle reliance on `dirP` ownership, and propagation of delegated error state. Test signals should cover open twice, non-FS paths with and without `fsChk`, delegated happy paths, and EBADF behavior before open.
