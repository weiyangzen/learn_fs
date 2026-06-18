# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_fs_sb.h

## Purpose

Defines CIFS superblock mount flags and `struct cifs_sb_info`, the CIFS per-superblock state container.

## Main Contents

- Mount flag bit definitions for permission behavior, uid/gid override, server inode numbers, direct I/O, xattr disable, special-character remapping, POSIX paths/ACLs, Unix emulation, byte-range lock behavior, CIFS ACLs, dynamic permissions, sync behavior, FS-Cache, Minshall+French symlinks, multiuser, strict I/O, PID forwarding, backup uid/gid intent, prefix-path mounting, SID-derived uid/mode, handle-cache disable, DFS disable, read-only/read-write cache assumptions, and shutdown state.
- `struct cifs_sb_info` fields:
  - tcon link tree and lock.
  - superblock tcon list link.
  - master tlink.
  - local NLS table.
  - parsed mount context.
  - active count and atomic mount flags.
  - delayed tlink pruning work.
  - RCU head.
  - optional prefix path.
  - serverino-autodisabled state.
  - root dentry after mount completion.

## Integration Notes

- The mount flags are consumed by path conversion, permission, cache, DFS, handle-cache, ACL, xattr, and I/O behavior throughout the CIFS client.
- `cifs_remap()` in `cifs_unicode.h` interprets the special-character remapping flags from this header.
