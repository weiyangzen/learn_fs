# sources/user-network-fs/samba/source3/smbd/dosmode.c

## Purpose
`dosmode.c` translates between Windows/DOS file attributes, UNIX mode bits, xattr-stored Samba DOS metadata, VFS DOS attribute hooks, compression/sparse flags, and file timestamp semantics.

## Important APIs, types, and functions
- `unix_mode()`, `apply_conf_file_mask()`, and `apply_conf_dir_mask()` derive UNIX modes for creates from DOS attributes and share masks.
- `fdos_mode()` returns DOS attributes for an open FSP, using fake-file handling, VFS DOS attributes, UNIX-mode fallback, name-based hidden rules, protocol filtering, compression, streams, symlinks, and cached attributes.
- `dos_mode_at_send()/recv()` asynchronously obtains attributes through VFS query-directory support and falls back to `fdos_mode()`.
- `parse_dos_attribute_blob()`, `fget_ea_dos_attribute()`, and `set_ea_dos_attribute()` decode/encode `SAMBA_XATTR_DOS_ATTRIB` NDR blobs including create time.
- `file_set_dosmode()` writes DOS attributes through VFS or UNIX chmod fallback.
- `file_set_sparse()`, `file_ntimes()`, `set_create_timespec_ea()`, and `get_create_timespec()` handle sparse flag and timestamp behavior.

## Control flow
On reads, `fdos_mode()` first rejects invalid stat data, handles fake files and non-regular/non-directory types, returns cached DOS attributes when present, asks the VFS for stored DOS attributes, or falls back to mapping UNIX mode bits. `dos_mode_post()` normalizes stream directory bits, compression, hidden-by-name/path, directory/normal defaults, and old protocol masks. On writes, `file_set_dosmode()` rejects read-only shares, symlinks, invalid temporary directories, and missing FSPs, then prefers `SMB_VFS_FSET_DOS_ATTRIBUTES()`. If unimplemented, it computes a UNIX mode, preserves file type/sticky/setuid/setgid and configured execute bits, protects setgid directory chmod rules, and optionally retries as root for DOS filemode semantics.

EA parsing supports multiple `xattr_DOSATTRIB` versions. New writes use version 5 with valid flags for attributes and create time. Attribute setting and time setting both support DOS semantics where write permission can allow changes that POSIX ownership would deny, subject to Samba configuration and access checks.

## State and persistence behavior
Persistent state can be stored in xattrs, UNIX mode bits, filesystem sparse/compression metadata through VFS, and timestamps. `smb_fname->st.cached_dos_attributes` caches computed attributes in memory. `set_create_timespec_ea()` persists create time by rewriting DOS attribute EA. Notifications are emitted on attribute changes and sparse changes.

## Dependencies and integration points
The file depends on loadparm mapping options, generated NDR xattr structures, VFS xattr/DOS/compression/time hooks, ACL access checks, fake files, lease notifications, DMAPI/offline handling through VFS defaults, and protocol selection from connection state. Directory enumeration and open/create paths consume these APIs.

## Risks and edge cases
- DOS attributes may be represented by xattrs or UNIX execute/write bits depending on configuration, making migration and mixed clients sensitive.
- Create time is stored in the same xattr as attributes; failed xattr writes can lose expected Windows metadata.
- Named streams inherit base file attributes except directory is stripped.
- Async VFS attribute failure semantics intentionally collapse many errors to last-resort mode mapping.
- Root fallback for chmod/xattr/time changes must remain gated by share write access and DOS semantics options.

## Test signals
Tests should cover DOS-to-UNIX create modes, readonly/archive/system/hidden mappings, xattr versions 1-5 parse/write including create time, old protocol filtering, stream attributes, symlink/reparse behavior, compression and sparse flags, async fallback paths, chmod root fallback, DOS file times, and notification emission.
