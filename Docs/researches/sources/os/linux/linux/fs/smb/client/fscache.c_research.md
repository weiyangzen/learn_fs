# File Research: sources/os/linux/linux/fs/smb/client/fscache.c

## Role

Implements CIFS integration with Linux FS-Cache for SMB share volumes and inodes.

## Key Logic

- `struct cifs_fscache_inode_key` defines the inode cache key from server unique ID, creation time, and file type. The comment notes it must match inode comparison logic in `cifs_find_inode()`.
- `cifs_fscache_fill_volume_coherency()` fills volume coherency metadata from tcon resource ID, volume creation time, and serial number.
- `cifs_fscache_get_super_cookie()` acquires a volume cookie once per tcon under `fscache_lock`. It supports IPv4/IPv6 server addresses, extracts and sanitizes the share name for the key, builds a key of the form `cifs,<address>,<share>`, attaches coherency data, handles `-EBUSY` collisions as nonfatal no-cache cases, and traces acquisition outcome.
- `cifs_fscache_release_super_cookie()` relinquishes the volume cookie with current coherency data and clears `tcon->fscache`.
- `cifs_fscache_get_inode_cookie()` builds an inode key/coherency tuple, acquires an FS-Cache cookie under the tcon volume, and marks the mapping for release callbacks when caching is active.
- `cifs_fscache_unuse_inode_cookie()` unuses a cookie, optionally updating coherency and file size.
- `cifs_fscache_release_inode_cookie()` relinquishes the inode cookie and clears the netfs cache pointer.

## Dependencies

Uses FS-Cache and netfs cookie APIs, CIFS inode/tcon/superblock structures, share-name extraction, socket address formatting, tracepoints, and CIFS debug logging.

## Research Notes

The volume key deliberately includes network endpoint and share name, while inode keys use server identity and creation time. Cache coherency is time-based for inodes and volume metadata-based for shares, so stale-data safety depends on server-provided IDs/timestamps being stable and comparable.
