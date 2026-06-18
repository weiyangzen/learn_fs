# File Research: sources/os/linux/linux-stable/fs/smb/client/fscache.c

## Summary
Implements CIFS integration with the Linux fscache/netfs cache API. It acquires and releases per-share cache volumes, acquires and releases per-inode cache cookies, and updates coherency metadata when inode cache cookies are unused or invalidated.

## Main Responsibilities
- Build stable fscache volume coherency data from tree-connection volume identity.
- Build stable inode cache keys from CIFS unique id, creation time, and file type.
- Acquire a fscache volume for a tree connection using server address and share name.
- Handle fscache volume key collisions without crashing the mount.
- Acquire inode cookies under the tree-connection volume cookie.
- Mark mappings as always needing release callbacks when inode cookies exist.
- Unuse inode cookies with optional coherency and size updates.
- Relinquish inode cookies during inode teardown.

## Key Interfaces
- `cifs_fscache_get_super_cookie()` acquires the share-level fscache volume.
- `cifs_fscache_release_super_cookie()` relinquishes the share-level volume with current coherency data.
- `cifs_fscache_get_inode_cookie()` acquires a per-inode fscache cookie.
- `cifs_fscache_unuse_inode_cookie()` stops using an inode cookie, optionally passing updated coherency data and file size.
- `cifs_fscache_release_inode_cookie()` relinquishes and clears the inode cookie.
- `cifs_fscache_fill_volume_coherency()` fills resource id, volume creation time, and serial number.

## Control Flow And Behavior
`cifs_fscache_get_super_cookie()` is idempotent through `tcon->fscache_acquired` and serialized by `tcon->fscache_lock`. It only accepts IPv4 and IPv6 server addresses. It extracts the share name from the tree name, replaces slash characters in the share component with semicolons, builds a volume key of the form `cifs,<server-address>,<share>`, fills volume coherency data, and calls `fscache_acquire_volume()`.

If the volume cookie is busy, the function logs a key collision, traces it, leaves `tcon->fscache` null, and still returns success so the mount can proceed without a usable cache volume. Other fscache acquisition errors are returned.

Inode cookie acquisition uses a packed key whose contents must match CIFS inode comparison logic: server unique id, creation time, and file type. Coherency data comes from inode ctime and mtime through the helper in `fscache.h`, and the current inode size is supplied to fscache.

## State And Synchronization
The tree connection stores `fscache_acquired`, `fscache`, and `fscache_lock`. Per-inode state is stored in `CIFS_I(inode)->netfs.cache`. The code relies on fscache/netfs cookie lifetime rules and on CIFS inode identity fields remaining stable for cached objects.

## Risks
Volume keys must be stable and unique enough across server address and share name; collisions disable caching for the tree connection. The inode key must stay synchronized with CIFS inode lookup semantics or cached data could be attached to the wrong inode. Coherency metadata is based on ctime/mtime, so server timestamp behavior affects cache reuse correctness.
