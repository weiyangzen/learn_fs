# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_iconv.c

## Purpose
Declares cd9660 iconv integration.

## Main Elements
- Includes kernel iconv and mount/module headers.
- Uses `VFS_DECLARE_ICONV(cd9660)`.

## Dependencies And Integration
Provides filesystem-level charset conversion hooks used by Joliet filename handling.

## Risk Notes
No runtime logic in this file; behavior depends on iconv support and callers in cd9660 utilities.
