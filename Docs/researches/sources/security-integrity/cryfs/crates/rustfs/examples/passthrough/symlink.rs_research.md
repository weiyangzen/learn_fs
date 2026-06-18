# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/symlink.rs

Purpose: Implements passthrough symlink reads.

Important APIs/types/functions: `PassthroughSymlink::new` stores a path. The `Symlink` impl reads the host symlink target and converts it to UTF-8 string.

Control flow: `target` calls `tokio::fs::read_link`, then `into_os_string().into_string()`; invalid Unicode becomes `FsError::CorruptedFilesystem`.

State and persistence behavior: no state beyond path. Target is stored by the host filesystem.

Dependencies and integration points: returned by `PassthroughNode::as_symlink` and symlink creation in `PassthroughDir`.

Risks: non-UTF-8 symlink targets are rejected even though Unix permits them. No validation in `as_symlink` means callers can construct this for non-symlinks until read fails.

Test signals: cover relative and absolute targets, non-UTF-8 targets on Unix, and wrong-node-type behavior.
