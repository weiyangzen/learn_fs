# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfstab.h

## Role

`vfstab.h` defines the user-facing `/etc/vfstab` parsing and formatting interface. It describes one filesystem table entry and declares lookup helpers for reading entries by special device, mountpoint, or matching template.

## Key Interfaces

The header defines:
- `VFSTAB` as `/etc/vfstab`.
- `VFS_LINE_MAX` as the maximum parsed line length.
- parse error codes `VFS_TOOLONG`, `VFS_TOOMANY`, and `VFS_TOOFEW`.
- `struct vfstab`, with string fields for special device, fsck device, mountpoint, filesystem type, fsck pass, automount flag, and mount options.

Convenience macros:
- `vfsnull(vp)` clears all fields to `NULL`.
- `putvfsent(fd, vp)` writes a vfstab entry, substituting `-` for missing fields.

## Integration Points

The declared library functions are:
- `getvfsent()`
- `getvfsspec()`
- `getvfsfile()`
- `getvfsany()`

These are consumed by userland mount/fsck administration tools rather than kernel VFS code.

## Research Notes

The interface stores pointers, not owned buffers, so callers must respect the parsing library’s lifetime rules. `putvfsent` is a macro around `fprintf`, so it evaluates its arguments directly and expects a valid `FILE *`.
