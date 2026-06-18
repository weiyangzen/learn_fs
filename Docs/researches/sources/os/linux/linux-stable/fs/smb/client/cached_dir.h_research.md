# File Research: sources/os/linux/linux-stable/fs/smb/client/cached_dir.h

## Purpose

Declares CIFS cached directory-handle and cached directory-entry structures plus the public cached-dir helper API.

## Main Contents

- `struct cached_dirent`
  - Represents one cached directory entry with name, length, logical position, and CIFS file attributes.
- `struct cached_dirents`
  - Holds per-open-file directory entry cache state, including validity/failure flags, associated file, mutex, expected position, entry list, and byte/entry accounting.
- `struct cached_fid`
  - Represents a cached directory FID with list membership, path, lease/open state, file-all-info validity, timestamps, kref, SMB FID, tcon, dentry, work items, cached dirents, and embedded `smb2_file_all_info`.
- `struct cached_fids`
  - Per-tcon cache container with spinlock, active and dying lists, laundromat delayed work, and aggregate directory-entry accounting.
- Declares global directory-cache byte accounting `cifs_dircache_bytes_used`.
- Defines `is_valid_cached_dir()` as `time && has_lease`.
- Declares open, close, drop, invalidate, free, and lease-break functions implemented in `cached_dir.c`.

## Integration Notes

- Includes only declarations and data shapes; actual locking/lifetime behavior is implemented in `cached_dir.c`.
- Structures are tightly coupled to CIFS tcon/session, SMB2 FID, lease, and file-all-info types.
