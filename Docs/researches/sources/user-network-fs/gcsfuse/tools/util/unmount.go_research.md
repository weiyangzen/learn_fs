# sources/user-network-fs/gcsfuse/tools/util/unmount.go

Purpose: retrying unmount helper for FUSE mount points.

Important APIs/types/functions: `Unmount(dir string) error`.

Control flow: calls `fuse.Unmount`; on success returns nil. If the error text contains `resource busy`, it logs, sleeps with exponential backoff factor 1.3 starting at 10 ms, and retries indefinitely. Other errors are wrapped and returned.

State/persistence behavior: mutates OS mount state by unmounting the target. No files are written.

Dependencies/integration: used by tools and tests that need robust cleanup, especially on OS X per comments.

Risks/test signals: indefinite retry on persistent resource-busy errors can hang callers. Matching is string-based rather than typed.
