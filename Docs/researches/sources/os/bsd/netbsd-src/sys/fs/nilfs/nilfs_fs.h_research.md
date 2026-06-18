# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_fs.h

This public NILFS on-disk format header defines file flags, bmap/B-tree layout, reserved inode numbers, inode structure, super-root structure, superblock structure, directory entries, segment summaries, DAT entries, checkpoint file entries, and segment-usage file entries.

The bmap definitions describe small direct maps stored inside the inode and larger hierarchical B-trees with `(dkey, dptr)` pairs. Dedicated inode numbers identify root, DAT, checkpoint, segment-usage, ifile, and reserved metadata files. `struct nilfs_inode` stores size, blocks, times, uid/gid, mode, link count, flags, bmap/device code, xattr pointer, and generation.

The super-root records CRC/size/flags/time and embeds DAT, CP, and SU metadata inodes. The superblock records disk revision, magic, CRC data, block/segment geometry, last checkpoint/partial segment/sequence, free blocks, timestamps, mount/check state, creator OS, default reserved uid/gid, inode and metadata-entry sizes, UUID, volume name, commit tuning, and reserved padding. Directory entries are ext2-like with 8-byte alignment.

Segment structures describe log-oriented NILFS partial segments: `nilfs_segment_summary`, per-file `nilfs_finfo`, virtual/DAT block-info records, segment flags, and minimum segment constraints. Metadata-file structures cover block group descriptors, DAT virtual-to-physical validity ranges, checkpoint/snapshot lists and flags, CP file header, segment usage flags, and SU file header.

Integration points: installed for userland tools and included by kernel NILFS code. It is the contract for parsing and constructing NILFS media, so fsck/newfs/mount/debug tools and kernel code must agree on these layouts and constants.

Risks: this is disk-format ABI. Field order, integer width, alignment, endian conversion, CRC byte-count macros, and offset macros must remain stable. The header contains several comments noting reserved/unknown/Linux-derived fields, so compatibility with Linux NILFS and older media depends on conservative interpretation.
