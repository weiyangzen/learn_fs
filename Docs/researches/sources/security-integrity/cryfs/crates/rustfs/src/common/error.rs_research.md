# sources/security-integrity/cryfs/crates/rustfs/src/common/error.rs

Purpose: central error taxonomy for filesystem operations, plus the `FsResult<T>` alias.

Important APIs: `FsError` covers custom errno values, not implemented, internal/corruption errors, descriptor misuse, node existence/type errors, overwrite errors, invalid path/operation, xattr buffer issues, and unsupported file type. `error_code` maps each error to libc errno. `From<Never>` converts unreachable lockable errors.

Control flow and state: errors are cloneable. Internal errors are stored in `Arc<anyhow::Error>` to preserve clone behavior. The adapters return `FsError` and backend adapters map to OS errors for FUSE replies.

Dependencies and integration: depends on `thiserror`, `libc`, `lockable::Never`, and `FileHandle`. Used by every trait and utility in the crate, including async drop bounds.

Risks and tests: mapping is security relevant because it controls user-visible POSIX behavior. `UnknownError` and `Custom` are broad escape hatches. TODOs call out the need for function-specific errors and richer context. `mkdir` tests verify several mappings such as ENOSYS, EEXIST, ENOENT, ENOTDIR, and EINVAL through the mounted backend.
