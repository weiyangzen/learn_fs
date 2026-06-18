# File Research: sources/os/linux/linux/fs/smb/client/fs_context.h

## Role

Private SMB client mount-context header. It defines mount-option enums, `struct smb3_fs_context`, parser exports, context lifecycle APIs, mount locking helpers, I/O size negotiation helpers, and symlink policy resolution.

## Key Definitions

- `cifs_errorf()` logs mount parsing errors to both `fs_context` and CIFS debug output.
- `cifs_io_align()` and `CIFS_ALIGN_{W,R,B}SIZE()` clamp zero or unaligned I/O sizes to page-aligned values and report the correction.
- Enums define SMB dialect tokens, cache flavors, reparse flavors, symlink flavors, security flavors, upcall targets, and every recognized mount option ID.
- `struct smb3_fs_context` stores all parsed mount state: identity and credential strings, UNC/source/prepath fields, NetBIOS names, addresses, UID/GID/mode settings, security/upcall type, dozens of boolean policy flags, negotiated and user-requested I/O sizes, cache timeouts, protocol ops/values, destination/source addresses, NLS state, snapshot/handle settings, multichannel fields, compression/rootfs/witness flags, DFS fields, reparse/symlink policy, native socket policy, DNS domain, and symlink root.

## Inline Logic

- `cifs_symlink_type()` resolves the effective symlink strategy from explicit `symlink=`, `mfsymlinks`, SFU emulation, Linux/POSIX extensions, and reparse settings.
- `smb3_fc2context()` returns `fc->fs_private`.
- `cifs_mount_lock()` / `cifs_mount_unlock()` wrap the global mount mutex.
- `cifs_negotiate_rsize()` and `cifs_negotiate_wsize()` ask protocol ops for negotiated sizes, cap user-provided sizes to negotiated maxima, enforce at least one page, and round down to page alignment.
- `cifs_negotiate_iosize()` negotiates read and write sizes together.

## Exposed API

Exports mount initialization/cleanup, context duplication, session password sync, mount flag update, and `cifs_sanitize_prepath()` for source path parsing.

## Dependencies

Includes CIFS global definitions plus Linux parser and fs-parser headers. The structure references CIFS session/tcon, protocol operation/value tables, NLS tables, sockets, and DFS session pointers.

## Research Notes

This header is the shared contract for SMB mount setup. Most fields are long-lived superblock policy, so duplication and cleanup in `fs_context.c` must stay synchronized with the string members defined here.
