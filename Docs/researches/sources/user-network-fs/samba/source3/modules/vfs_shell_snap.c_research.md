# sources/user-network-fs/samba/source3/modules/vfs_shell_snap.c

## Purpose
`vfs_shell_snap.c` implements Samba snapshot-management hooks by invoking administrator-configured shell commands. It does not implement snapshot I/O; it provides check/create/delete plumbing for external snapshot tooling.

## Important APIs, Types, And Functions
- `shell_snap_check_path()` runs `shell_snap:check path command <service_path>` and returns the service path as the base volume on success.
- `shell_snap_create()` runs `shell_snap:create command <base_volume>`, reads stdout, and expects a single snapshot path line.
- `shell_snap_delete()` runs `shell_snap:delete command <base_path> <snap_path>`.
- `shell_snap_fns` registers snap check/create/delete hooks.

## Control Flow
Each hook reads its configured command from the service parameters. Missing commands return `NT_STATUS_NOT_SUPPORTED`. Create uses `smbrun` with stdout captured to an fd, reads bounded lines via `fd_lines_load`, and copies base/snapshot paths to caller memory. Delete and check use command exit status only.

## State And Persistence
The module stores no state. Persistent effects are entirely produced by external commands.

## Dependencies And Integration Points
It depends on `smbrun`, Samba parameter lookup, `fd_lines_load`, and snapshot-management VFS hooks. It registers as `shell_snap`.

## Risks
- Command strings are concatenated with paths without shell escaping in this file; safe configuration and trusted paths are critical.
- Create assumes the first output line is the snapshot path and ignores extra semantics.
- Exit-code-only check/delete may not distinguish unsupported, permission denied, and transient failures.

## Test Signals
- Configure harmless scripts for check/create/delete and verify hook statuses and returned paths.
- Test missing command parameters and nonzero exits.
- Test snapshot path output with empty, long, and multiple-line stdout.
- Validate behavior with service paths containing spaces or shell metacharacters in a controlled environment.
