# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.8.in

## Purpose

Manual page template for `ntfs-3g`, `mount -t ntfs-3g`, `lowntfs-3g`, and `mount -t lowntfs-3g`. It documents command syntax, driver capabilities, safety requirements, mount options, user mapping, examples, exit codes, known issues, authors, and related tools.

## Documented Driver Capabilities

The man page describes NTFS-3G as a read/write NTFS driver supporting:

- Create/remove/rename/move files and directories.
- Hard links and streams.
- Sparse files.
- Transparent reads/writes of compressed files.
- Special files such as symlinks, devices, and FIFOs.
- Ownership and permissions, including POSIX ACLs.
- Alternate Data Streams through selected interfaces.

It notes there are two variants, `ntfs-3g` and `lowntfs-3g`, with option-specific differences.

## Safety Guidance

- Windows must be fully shut down before Linux mounts internal NTFS filesystems.
- Windows hibernation and fast restart can leave volumes inconsistent.
- The recommended Windows command is `powercfg /h off`.
- Hibernated or fast-restart-affected internal disks are forced read-only unless explicit risky options are used.

## Access and Filename Semantics

- By default, mounted files are owned by the mounting process uid/gid and everyone has broad permissions.
- `uid`, `gid`, `umask`, `fmask`, and `dmask` can override global ownership/masks.
- `permissions` enables POSIX-like ownership and access control.
- User mapping connects Linux uid/gid to Windows SIDs.
- NTFS supports DOS, Win32, and POSIX namespaces; NTFS-3G creates POSIX namespace names by default.
- `windows_names` enforces Windows filename restrictions on new names.

## Alternate Data Streams

- Every file has an unnamed stream and may have named streams.
- By default, only unnamed data is read directly.
- `streams_interface=windows` exposes named streams as colon syntax, but not with `lowntfs-3g`.
- `streams_interface=xattr` exposes named streams as extended attributes.
- `ntfs.streams.list` can list named data streams.

## Main Options Documented

- `acl`: enable POSIX ACLs where supported.
- `allow_other`: allow access by users other than the mounter.
- `atime`, `noatime`, `relatime`: access-time policy; `relatime` is default.
- `big_writes`: avoid splitting writes into 4 KiB chunks where supported.
- `compression` / `nocompression`: control creation of compressed files in compressed directories.
- `debug`: verbose libntfs-3g and FUSE output.
- `delay_mtime[=value]`: delay mtime/ctime updates until close or delay threshold.
- `dmask`, `fmask`, `umask`: permission masks.
- `efs_raw`: backup/restore encrypted files without decrypting them.
- `force`: obsolete; superseded by `recover` and `norecover`.
- `hide_dot_files`: set NTFS hidden flag for dot-prefixed created names.
- `hide_hid_files`: omit NTFS-hidden files from directory listings.
- `ignore_case`: lowntfs-3g only; case-insensitive access with lowercase directory listings.
- `inherit`: use Windows inheritance rules for initial protections.
- `locale`: locale override, discouraged because untranslatable names may become invisible.
- `max_read`: maximum read operation size.
- `no_def_opts`: cancels default `silent`, `allow_other`, and `nonempty`.
- `no_detach`: stay attached to terminal.
- `norecover` / `recover`: control recovery of improperly unmounted Windows volumes; `recover` is default.
- `remove_hiberfile`: delete Windows hibernation file, losing saved session state.
- `ro`: read-only mount.
- `show_sys_files`: show NTFS metafiles in directory listings.
- `silent`: ignore chmod/chown/permission-check errors when permissions are not enabled.
- `special_files=interix|wsl`: choose special-file representation mode.
- `streams_interface=none|windows|xattr`: named stream access mode.
- `uid`, `gid`: global numeric owner/group.
- `usermapping=file-name`: custom SID mapping file.
- `user_xattr`: alias for `streams_interface=xattr`.
- `windows_names`: reject new names invalid on Windows.

## User Mapping Section

- Default mapping file is `.NTFS-3G/UserMapping` on the NTFS partition.
- `usermapping=` can specify absolute or partition-relative alternate mapping.
- Mapping file lines have `uid:gid:SID`.
- uid and gid are optional.
- A default SID-only mapping can be used when Windows interoperation is not required.
- Strong Windows interoperation needs mappings for each shared user/group.
- `ntfsusermap` can generate mapping files.
- With a user mapping file, `uid=`, `gid=`, masks, and `silent` are ignored.

## Examples

The page includes examples for:

- Mounting `/dev/sda1` at `/mnt/windows`.
- Using `mount -t ntfs-3g`.
- Mounting with `permissions`.
- Read-only mount with `uid=1000`.
- `/etc/fstab` entry.
- Unmounting with `umount`.

## Exit Codes and References

- Exit code `0` means success.
- Other unique error codes are documented in `ntfs-3g.probe(8)`.
- Known issues point to the NTFS-3G FAQ and GitHub issue tracker.
- See also:
  - `ntfs-3g.probe(8)`
  - `ntfsprogs(8)`
  - `attr(5)`
  - `getfattr(1)`

## Role in Source Tree

This file is the operator-facing contract for the FUSE drivers built in `src/`. It documents many behaviors implemented in `ntfs-3g.c`, `lowntfs-3g.c`, and `ntfs-3g_common.c`, especially mount safety, permissions, alternate streams, hibernation handling, and special-file compatibility.
