# File Research: sources/os/linux/linux/fs/hpfs/hpfs.h

Purpose: Defines HPFS on-disk structures, constants, bitfields, and helper predicates.

Key content:
- Sector-number typedefs for fnodes, dnodes, and anodes.
- Boot block, super block, spare block, bad block, hotfix, and codepage structures.
- Bitmap layout documentation for 8 MiB bands and the directory band.
- `struct dnode` and `struct hpfs_dirent` for directory B-tree nodes and entries.
- B+ tree structures for file allocation: leaf extents and internal anode pointers.
- `struct fnode` for file/directory allocation roots and EA metadata.
- `struct anode` for allocation subtrees.
- `struct extended_attribute` and EA flag helpers.

Dependencies and integration:
- Included by `hpfs_fn.h`, which is then used throughout HPFS.
- Encodes little-endian on-disk layout and bitfields conditional on CPU endian.

Risk notes:
- Comments state parts of HPFS are inferred/guesswork; defensive validation elsewhere is important.
- On-disk bitfields and packed flexible layouts are sensitive to compiler layout and endian behavior.
