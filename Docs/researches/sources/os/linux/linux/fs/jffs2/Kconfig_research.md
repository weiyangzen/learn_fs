# File Research: sources/os/linux/linux/fs/jffs2/Kconfig

## Role

This file declares Linux Kconfig options for building and configuring JFFS2, the Journalling Flash File System v2 for MTD flash devices.

## Main Configuration Symbols

- `JFFS2_FS`: main tristate filesystem option; depends on `MTD` and selects `CRC32`.
- `JFFS2_FS_DEBUG`: integer debug verbosity, default `0`.
- `JFFS2_FS_WRITEBUFFER`: write-buffer support, default enabled; required for NAND, NOR with transparent ECC, and DataFlash.
- `JFFS2_FS_WBUF_VERIFY`: optional readback verification of write-buffer writes.
- `JFFS2_SUMMARY`: optional summary-node support for faster mount.
- `JFFS2_FS_XATTR`: extended attribute support.
- `JFFS2_FS_POSIX_ACL`: POSIX ACL support; depends on xattrs, defaults enabled, selects `FS_POSIX_ACL`.
- `JFFS2_FS_SECURITY`: security-label xattr support; depends on xattrs, defaults enabled.
- Compression options for zlib, LZO, RTIME, and Rubin compressors.

## Compression Configuration

`JFFS2_COMPRESSION_OPTIONS` exposes advanced compressor selection. Without it, conservative defaults apply:
- Zlib default enabled.
- RTIME default enabled.
- LZO default disabled.
- Rubin default disabled.

The default compression mode choice includes:
- `JFFS2_CMODE_NONE`
- `JFFS2_CMODE_PRIORITY`
- `JFFS2_CMODE_SIZE`
- `JFFS2_CMODE_FAVOURLZO`

## Integration

The symbols declared here drive conditional compilation in `fs/jffs2/Makefile` and feature availability in the JFFS2 implementation. Xattr, ACL, security label, compressor, write-buffer, and summary code are all included based on these options.

## Important Invariants

- JFFS2 is restricted to MTD devices, not normal block devices.
- POSIX ACL support is layered on xattr support.
- Removing compressors may make existing filesystems unreadable.
- Enabling experimental/less common compressors can reduce compatibility with older kernels or bootloaders.

## Research Notes

This file is the feature gate for the JFFS2 source directory. Most runtime subsystems in this group (`acl.c`, background GC, build/mount code) depend on the base `JFFS2_FS`, while ACL code is only built with `JFFS2_FS_POSIX_ACL`.
