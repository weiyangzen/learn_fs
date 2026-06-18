# File Research: sources/os/bsd/netbsd-src/sys/sys/fstypes.h

Read completely: 299 lines.

## Purpose
Defines filesystem IDs, file handles, mount flags, exported/internal flag descriptions, visibility masks, and sync wait modes.

## Main Interfaces
- `fsid_t`.
- Kernel file handles: `struct fid`, `struct fhandle`, `fhandle_t`, `FHANDLE_SIZE_*`, `FHANDLE_*` helpers.
- Basic mount flags: `MNT_RDONLY`, `MNT_SYNCHRONOUS`, `MNT_NOEXEC`, `MNT_NOSUID`, `MNT_NODEV`, `MNT_UNION`, `MNT_ASYNC`, `MNT_RELATIME`, `MNT_DISCARD`, `MNT_EXTATTR`, `MNT_LOG`, `MNT_NOATIME`, `MNT_AUTOMOUNTED`, `MNT_SOFTDEP`, etc.
- Export flags: `MNT_EXRDONLY`, `MNT_EXPORTED`, `MNT_DEFEXPORTED`, `MNT_EXPORTANON`, `MNT_EXKERB`, `MNT_EXNORESPORT`, `MNT_EXPUBLIC`.
- Internal flags: `MNT_LOCAL`, `MNT_QUOTA`, `MNT_ROOTFS`; `IMNT_*`.
- Masks/lists: `MNT_BASIC_FLAGS`, `MNT_VISFLAGMASK`, `MNT_OP_FLAGS`, `__MNT_FLAG_BITS`, `__IMNT_FLAG_BITS`.
- Wait modes: `MNT_WAIT`, `MNT_NOWAIT`, `MNT_LAZY`.

## Dependencies And Integration
Used by mount, statvfs, export/NFS filehandle code, VFS sync/unmount, and filesystem flag parsing/display.

## Risks And Edge Cases
- The header warns flags are not in numeric order and new flags should reuse unused bits.
- Some bits are shared/synonymous, such as `MNT_EXKERB` and `MNT_POSIX1EACLS`.
- Filehandle size is variable but bounded by max/min compatibility constants.

## Filesystem Relevance
High. Defines core mount and filehandle ABI/state used by VFS and filesystems.
