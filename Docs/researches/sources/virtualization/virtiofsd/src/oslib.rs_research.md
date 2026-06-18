# File Research: sources/virtualization/virtiofsd/src/oslib.rs

## Scope

Linux OS/syscall wrapper layer used by sandboxing, passthrough path handling, migration, and file I/O.

## APIs Covered

- `OsFacts` probes `openat2` support.
- Safe-ish wrappers for `mount`, `umount2`, `fchdir`, `fchmod`, `fchmodat`, `umask`, `openat`, `open_tree`, `move_mount`, and constrained `openat2`.
- `ScopedUmask` restores the previous umask on drop.
- File-handle bindings: `CFileHandle`, `name_to_handle_at`, `open_by_handle_at`.
- `WritevFlags`, `ReadvFlags`, `writev_at`, `readv_at`.
- `PipeReader`, `PipeWriter`, `pipe`.
- Per-thread effective credential syscalls: `seteffuid`, `seteffgid`, `setsupgroup`, `dropsupgroups`.

## Behavior

- `do_open_relative_to()` uses `RESOLVE_IN_ROOT | RESOLVE_NO_MAGICLINKS` plus caller flags to restrict path traversal relative to a directory FD.
- `CFileHandle` converts from serialized file handles and limits handle byte size to 128.
- `preadv2`/`pwritev2` wrappers expose newer RWF flags including noappend, atomic, and dontcache where libc provides them.
- Credential helpers call syscalls directly to avoid libc’s process-wide credential synchronization.

## Risks

Correct safety depends on valid C strings, FDs, iovec pointers, and syscall availability. These wrappers sit on the security boundary for path traversal, sandbox setup, and guest-credential impersonation.
