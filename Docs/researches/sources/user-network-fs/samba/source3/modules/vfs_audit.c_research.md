# sources/user-network-fs/samba/source3/modules/vfs_audit.c

## Purpose
`vfs_audit.c` is a small Samba VFS module that logs selected share and file operations to syslog. It wraps the next VFS implementation for connect, disconnect, mkdir, open, close, rename, unlink, and chmod, emitting an audit record that includes the target path, file descriptor where available, failure status, and `errno` text.

## Important APIs, types, and functions
- `audit_syslog_facility()` maps the `audit:facility` smb.conf parameter through platform-available `LOG_*` values, defaulting to `LOG_USER`.
- `audit_syslog_priority()` maps `audit:priority` to syslog priorities, defaulting to `LOG_NOTICE` and falling back to `LOG_WARNING` for invalid values.
- `audit_connect()` delegates to `SMB_VFS_NEXT_CONNECT()`, calls `openlog("smbd_audit", LOG_PID, facility)`, and logs the service/user connection.
- `audit_mkdirat()`, `audit_renameat()`, and `audit_unlinkat()` build displayable full paths with `full_path_from_dirfsp_atname()` before delegating.
- `audit_openat()`, `audit_close()`, and `audit_fchmod()` log handle-oriented operations using `fsp_str_dbg()`, `fsp_get_pathref_fd()`, and `fsp->fsp_name`.
- `vfs_audit_fns` registers the wrapped VFS entry points, and `vfs_audit_init()` registers the module under the name `audit`.

## Control flow
The module is a pass-through wrapper. Each operation calls the corresponding `SMB_VFS_NEXT_*` function, then logs success or failure. Path-based operations first allocate full `smb_filename` objects so the log line records the resolved path rather than only the relative component. `audit_renameat()` preserves the original failure `errno` across talloc cleanup so callers see the next-module error unchanged. `audit_connect()` only starts syslog logging after the lower connect succeeds; `audit_disconnect()` logs before passing disconnect down the stack.

## State and persistence behavior
There is no persistent module-owned state. Configuration is read dynamically from loadparm for each log event, and all durable output is external syslog data. Temporary `smb_filename` allocations are freed after each operation. The module does not alter file state except through the delegated VFS calls.

## Dependencies and integration points
The module depends on Samba's VFS dispatch layer, `smbd/smbd.h`, loadparm helpers, talloc-backed `smb_filename` helpers, and the platform syslog API. It is declared in `source3/modules/wscript_build` as `vfs_audit` and integrates by adding `audit` to a share's `vfs objects`.

## Risks and edge cases
- Logging happens after most file operations, so failure logging depends on preserving `errno` correctly; `audit_mkdirat()` and `audit_unlinkat()` do not explicitly save `errno` across `syslog()`/cleanup.
- Log contents include raw paths and user/service names, so deployments must treat syslog as sensitive audit data.
- Facility availability is compile-time platform dependent because many `LOG_*` values are guarded by `#ifdef`.
- The module covers only a small set of operations and should not be mistaken for complete file activity auditing.

## Test signals
There are no targeted tests for this file in the inspected module tree. Practical validation is configuration-driven: load the module on a test share, exercise connect/open/close/create/rename/unlink/chmod paths, and confirm syslog facility/priority mapping plus error propagation. Build registration in `wscript_build` is the static integration signal.
