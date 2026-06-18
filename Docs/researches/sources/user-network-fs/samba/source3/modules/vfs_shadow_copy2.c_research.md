# sources/user-network-fs/samba/source3/modules/vfs_shadow_copy2.c

## Purpose
`vfs_shadow_copy2.c` is the richer shadow-copy implementation. It exposes filesystem snapshots as Windows Previous Versions by translating SMB `@GMT` timestamp references (`smb_filename->twrp`) into snapshot filesystem paths, enumerating snapshots from configurable snapshot directories, and blocking writes into snapshots.

## Important APIs, Types, And Functions
- `struct shadow_copy2_config` stores `shadow:*` parameters: timestamp format, sscanf/localtime mode, snapdir, delimiter, snapdirseverywhere, crossmountpoints, fixinodes, sort order, mount point, relative connect path, and snapshot base path.
- `struct shadow_copy2_private` stores config, cached regex snaplist, `shadow_cwd`, and connectpath state.
- Path conversion helpers: `shadow_copy2_strip_snapshot_internal`, `check_for_converted_path`, `shadow_copy2_do_convert`, `shadow_copy2_convert`, `shadow_copy2_insert_string`, `shadow_copy2_snapshot_path`, and `make_path_absolute`.
- Snapshot enumeration helpers: `shadow_copy2_find_snapdir`, `shadow_copy2_snapshot_to_gmt`, `shadow_copy2_get_shadow_copy_data`, and sorting helpers.
- VFS wrappers cover stat/lstat/fstat/fstatat/open/readlink/realpath/disk_free/quota/DFS/parent_pathname and deny rename/link/symlink/unlink/mkdir/mknod/chmod/chflags/fsetxattr/fntimes into snapshots.
- `shadow_copy2_connect()` parses and validates configuration and registers private state.

## Control Flow
Connect delegates first, allocates private state, reads `shadow:*` parameters, validates incompatible combinations, discovers or validates mountpoint/basedir/snapsharepath, computes `snapshot_basepath`, trims path strings, and stores handle data. For reads and metadata, wrappers inspect `twrp` or already-converted paths. If no timestamp is present, they delegate and optionally adjust inode values for converted snapshot paths. If a timestamp exists, they strip the SMB-layer snapshot marker, convert the requested path to a backend snapshot path, delegate using the converted name, and then restore caller-visible objects. Mutating operations detect timestamp or converted snapshot paths and fail with `EROFS` or `EXDEV`. Enumeration opens the discovered snapshot directory, verifies list permission, converts backend snapshot names to `@GMT` labels, optionally caches regex-based names, and sorts labels.

## State And Persistence
Per-connection state holds configuration, current shadow CWD, and a cached snapshot list for regex mapping. Persistent snapshots are external filesystem directories. The module can alter returned inode numbers when `shadow:fixinodes = yes` by hashing the snapshot path into high inode bits, but it does not modify files.

## Dependencies And Integration Points
It depends on Samba VFS path, open, stat, directory, DFS, quota, and parent-pathname APIs; `ntioctl` shadow-copy structures; TDB Jenkins hash for inode adjustment; POSIX regex; and loadparm. It is intended for stacking where snapshot directories are visible in the local filesystem and registers as `shadow_copy2`.

## Risks
- Path conversion is complex and highly configuration-sensitive; absolute snapdir, snapdirseverywhere, basedir, mountpoint, and snapsharepath interactions can produce surprising paths.
- Snapshot write protection relies on all mutating hooks being covered; missing hooks could allow writes through a snapshot path.
- Cached regex snapshot names must refresh when requested timestamp is newer than fetch time.
- The code sometimes maps conversion failures to `ENOMEM` even when the underlying condition is not memory-related.
- `fixinodes` reduces but does not eliminate inode collision risk.

## Test Signals
- Enumerate snapshots with `shadow:format`, `shadow:snapdir`, sorting, regex prefix/delimiter, and labels/no-labels calls.
- Open/stat/read files through SMB Previous Versions and verify backend path conversion for classic and `snapdirseverywhere` layouts.
- Attempt writes, renames, xattrs, mkdir, DFS create, and unlink through `@GMT` paths and verify `EROFS`/write-protected behavior.
- Test absolute snapdir, mountpoint, basedir, snapsharepath, and crossmountpoints combinations.
- Verify `fixinodes` changes returned inode values only for snapshot paths.
