# File Research: sources/os/linux/linux/fs/smb/client/fscache.h

## Role

Header for CIFS FS-Cache integration. It defines coherency payloads and provides either real FS-Cache declarations/helpers or no-op stubs when `CONFIG_CIFS_FSCACHE` is disabled.

## Key Definitions

- `struct cifs_fscache_volume_coherency_data` stores packed resource ID, volume creation time, and volume serial number.
- `struct cifs_fscache_inode_coherency_data` stores mtime/ctime seconds and nanoseconds as little-endian fields.
- With `CONFIG_CIFS_FSCACHE`, the header declares super-cookie and inode-cookie lifecycle functions implemented in `fscache.c`.

## Inline Helpers

- `cifs_fscache_fill_coherency()` derives inode coherency metadata from VFS ctime and mtime.
- `cifs_inode_cookie()` returns the netfs cookie from `CIFS_I(inode)->netfs`.
- `cifs_invalidate_cache()` invalidates the cookie with current coherency and file size.
- `cifs_fscache_enabled()` checks whether the inode cookie is enabled.
- Without FS-Cache support, all lifecycle, invalidation, and enabled checks compile to no-op or false/null helpers.

## Dependencies

Includes Linux swap and fscache headers plus CIFS global structures.

## Research Notes

This header lets the rest of the SMB client call cache helpers unconditionally. The conditional stubs keep file I/O code simple while making the feature entirely optional at build time.
