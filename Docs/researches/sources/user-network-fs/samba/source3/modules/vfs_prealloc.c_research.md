# sources/user-network-fs/samba/source3/modules/vfs_prealloc.c

## Purpose
`vfs_prealloc.c` preallocates disk extents for newly created or truncated files based on filename extension. It targets XFS-style reservation APIs so large expected files can be laid out more efficiently without immediately changing logical file size.

## Important APIs, Types, And Functions
- `preallocate_space()` issues `XFS_IOC_RESVSP64`, `F_RESVSP64`, or fails with `ENOSYS` depending on platform support.
- `prealloc_connect()` loads `prealloc:debug`.
- `prealloc_openat()` checks `O_CREAT`/`O_TRUNC`, extracts a lowercase extension up to nine characters, reads `prealloc:<ext>`, opens the file, stores the requested size as an FSP extension, and preallocates.
- `prealloc_ftruncate()` delegates truncate then reapplies the saved preallocation.

## Control Flow
Only create/truncate-oriented opens are eligible. The extension is parsed from `smb_fname->base_name`, converted to lowercase, and used as a loadparm key. If no configured positive size exists, open passes through. If configured, the file is opened first, an FSP extension stores the size, and the reservation call runs. Truncate reuses that extension to restore the reserved allocation after logical size changes.

## State And Persistence
The module has global `module_debug` and per-open FSP extension state containing the reservation size. Reservations are filesystem allocation state, not Samba metadata; `RESVSP` is chosen so reservation should not inflate `st_size`.

## Dependencies And Integration Points
It depends on Samba VFS open/truncate hooks, loadparm parsing, and platform XFS/fcntl reservation APIs. It registers as `prealloc` and is configured with keys like `prealloc:mpeg = 500M`.

## Risks
- There is a suspicious `if (!ok); goto normal_open;` pattern after `strlower_m(fext)` that makes normal-open flow unconditional in that block; this should be treated as a bug signal when reviewing behavior.
- Platform support is conditional; unsupported builds silently fail reservation with debug logging.
- Extension length is capped at `sizeof(fext) - 1`.
- Reservation failures remove the FSP extension, so later truncate will not retry.

## Test Signals
- Configure a matching extension and verify reservation syscall occurs on create/truncate opens.
- Verify nonmatching, long-extension, and read-only opens bypass preallocation.
- Test truncate after preallocated open and confirm reservation is reissued.
- Build/test on platforms with and without XFS reservation support.
