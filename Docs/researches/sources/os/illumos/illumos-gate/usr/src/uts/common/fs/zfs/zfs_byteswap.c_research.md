# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_byteswap.c

Provides endian conversion routines for ZFS on-disk znode and ACL data. These are used when importing or reading metadata written with byte order different from the host.

`zfs_oldace_byteswap()` swaps arrays of old fixed-size `ace_t` entries. `zfs_oldacl_byteswap()` treats the whole supplied buffer as fixed old ACE slots because the old layout does not independently encode how many valid ACEs are present.

`zfs_ace_byteswap()` handles both POSIX `ace_t` layout and ZFS FUID ACL layout. It walks the supplied byte buffer, swaps ACE header fields, chooses the entry size based on special owner/group/everyone compact entries, normal FUID entries, and object ACE entries, and avoids overrunning partially filled embedded ACL blocks. For ZFS-layout entries it swaps `z_fuid` only when the full `zfs_ace_t` body is present.

`zfs_acl_byteswap()` is the public wrapper for modern ZFS ACL layout. `zfs_znode_byteswap()` swaps every fixed-width field in `znode_phys_t`, including timestamps, mode, size, parent, link count, xattr, rdev, flags, uid/gid/FUIDs, ZAP object, padding, and embedded ACL physical metadata. It then dispatches to modern or old ACL byteswapping based on the swapped ACL version.

The main safety concern addressed here is bounded parsing of variable-sized ACE records inside fixed-size znode bonus data; short trailing fragments are ignored rather than read past the buffer.
