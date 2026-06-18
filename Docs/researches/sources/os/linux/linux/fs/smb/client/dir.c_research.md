# File Research: sources/os/linux/linux/fs/smb/client/dir.c

## Purpose
Implements CIFS/SMB VFS dentry and directory-name operations: path construction, lookup, create, atomic open, mknod, tmpfile creation, negative dentry revalidation, case-insensitive dentry hashing/comparison, and silly-rename path generation.

## Main Interfaces
- Path builders: `cifs_build_path_to_root()`, `build_path_from_dentry()`, `build_path_from_dentry_optional_prefix()`, `__build_path_from_dentry_optional_prefix()`.
- Create/open: `cifs_atomic_open()`, `cifs_create()`, `cifs_tmpfile()`.
- Lookup and node creation: `cifs_lookup()`, `cifs_mknod()`.
- Dentry operations: `cifs_dentry_ops`, `cifs_ci_dentry_ops`.
- Misc path helper: `cifs_silly_fullpath()`.

## Control Flow
Path builders combine raw dentry paths with optional superblock prepaths and optional DFS tree-name prefixes, converting separators according to mount flags. `check_name()` rejects overly long path components and disallows backslashes when POSIX paths are not enabled.

Create/open flows use `cifs_sb_tlink()` to obtain the right tcon, generate lease keys when supported, record pending opens, and call `__cifs_do_create()`. That helper tries legacy POSIX open when enabled and applicable, otherwise uses dialect `open()` with SMB create options, requested access, create disposition, optional parent lease key, fscache read-for-write behavior, and mode handling. It then queries inode information and validates the resulting inode type.

Lookup builds the full path and queries inode metadata using POSIX, Unix, or normal CIFS inode-info paths depending on negotiated extension support. Negative dentry handling can rely on a fully cached parent directory when case-insensitive lookup is forced.

`cifs_tmpfile()` creates a hidden temporary SMB2+ file with delete-on-close semantics, gives it a generated name, instantiates an unhashed dentry, and marks temporary/hidden attributes.

## State And Synchronization
- Uses tcon links from the superblock to support multiuser mounts.
- Uses pending-open tracking around network creates.
- Updates parental dentry timestamp caches after successful lookups.
- Dentry revalidation may force inode revalidation by clearing `CIFS_I(inode)->time`.
- Case-insensitive dentry ops hash and compare via the mount codepage and `cifs_toupper()`.

## Integration Points
- Calls dialect operations for open, close, make-node, set-file-info, and lease-key handling.
- Uses inode metadata helpers from the CIFS client for Unix, POSIX SMB3.11, and normal SMB queries.
- Uses fscache helpers to request and invalidate cache state.
- Uses cached directory handles from `cached_dir.h` for negative lookup optimization and parent lease keys.
- Uses DFS automount flagging through `cifs_d_automount` in dentry ops.

## Notable Behaviors
- Write-only opens may request read access when fscache is enabled so partial writes can fill cache gaps; if access is denied, the code retries without read and invalidates cache.
- `O_TMPFILE` is supported only for SMB2 and later.
- Parent directory cached handles can supply parent lease keys to SMB2 create and are invalidated before use.
- Dentry revalidation sets `DCACHE_NEED_AUTOMOUNT` if refreshed inode attributes reveal an automount/DFS entry.
- Negative dentries are dropped for create and rename-target lookups to preserve caller spelling and case semantics.

## Risks And Review Focus
- Path construction is sensitive to DFS prefixing, prepath ownership, POSIX path flags, and separator conversion.
- Create error paths must close remote handles, remove pending opens, release tlinks, and free open info exactly once.
- Cached-directory negative lookup assumptions depend on mount case-sensitivity behavior.
- Temporary and silly names use bounded retry loops; failure handling must preserve VFS expectations for unhashed or negative dentries.
