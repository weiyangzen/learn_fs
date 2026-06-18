# sources/user-network-fs/davfs2/src/umount_davfs.c

## Purpose
`umount_davfs.c` is the unmount helper for davfs2. It delegates the actual unmount to the platform `umount` command, but waits for the associated `mount.davfs` daemon process to terminate so dirty cached files can be synchronized before the user’s `umount` returns.

## Important APIs, Types, and Functions
- `main(int argc, char **argv)`: parses helper options, canonicalizes the mountpoint, derives the davfs pidfile name, validates that the pid belongs to a `PROGRAM_NAME` process, invokes `umount`, and polls process termination.
- `UMOUNT_CMD`: `"umount -i"` on Linux to avoid recursive helper invocation, `"umount"` on FreeBSD.
- Uses `mcanonicalize_file_name()` from `util.h` and Neon string helpers for concatenation.

## Control Flow
The program accepts version/help options and ignores common `umount` flags passed by the real `umount`. It requires exactly one mountpoint argument. If canonicalization fails, it warns and runs `umount` anyway. Otherwise it converts the canonical mountpoint into the pidfile naming scheme used by `mount_davfs.c`, reads the pid, verifies via `ps -p <pid>` that a matching davfs process exists, then runs `umount`. If unmount succeeds, it prints progress dots while polling `ps` every three seconds until the daemon disappears.

## State and Persistence
The helper reads, but does not remove, the pidfile under `DAV_SYS_RUN`. It constructs shell command strings for both `umount` and `ps`, and its only long-lived state is process existence. Cleanup of pidfile/cache state remains the mount daemon’s responsibility.

## Dependencies and Integration Points
It integrates with the system `umount` tool and process table, davfs runtime pidfile naming, `defaults.h` for directories/program names, `util.h` for fatal/warning behavior, i18n, and Neon allocation/string helpers.

## Risks and Edge Cases
The code uses `system()` and `popen()` with shell-constructed strings. The mountpoint is single-quoted, but embedded single quotes in a path would break shell quoting and could become a command injection vector. `fscanf(file, "%s[0-9]", pid)` does not implement a digit-only scanset as likely intended; it reads a whitespace-delimited token into a fixed 32-byte buffer without width, so malformed pidfiles could overflow. `ps` output is matched by substring for pid and program name, which can be imprecise. If verification fails, it still unmounts and leaves manual cleanup to the user.

## Test Signals
Tests should cover help/version, missing/extra arguments, canonicalization failure fallback, pidfile name parity with `mount_davfs.c`, malformed/missing pidfiles, nonexistent daemon, failed `umount`, and successful wait-loop completion. Security tests should include mountpoints containing quotes or shell metacharacters and overlong pidfile content.
