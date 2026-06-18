# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_bmap.c

This file implements FreeVxFS logical-to-physical block mapping for internal reads and VFS address-space operations.

Major responsibilities:
- Map ext4-style VxFS extents with direct extent descriptors and one indirect extent path.
- Map typed extents, including recursive traversal through indirect typed extent blocks.
- Reject or warn about unsupported immediate, none, and external-device typed extent organizations.
- Provide the public internal mapper `vxfs_bmap1()`.

Important design points:
- `vxfs_bmap_ext4()` treats VxFS "ext4" organization as a traditional direct-plus-indirect extent layout, unrelated to Linux ext4.
- `vxfs_bmap_typed()` walks inline typed extent descriptors and delegates indirect descriptors to `vxfs_bmap_indir()`.
- Typed extent headers encode type in the high bits and logical offset in the low bits.
- `VXFS_TYPED_DEV4` descriptors are recognized only enough to report unsupported external-device mappings.
- The mapper returns physical block zero on failure, which downstream read helpers treat as I/O failure or unmapped data.

Key invariants:
- All multi-byte on-disk fields are converted with the superblock byte-order helpers.
- Unsupported organization types must not be mapped.
- Indirect extent size larger than the filesystem block size is rejected.
- Unknown typed extent types trigger `BUG()`, reflecting an assumption that mounted metadata was already coherent enough for read-only traversal.

External interfaces:
- Exports `vxfs_bmap1()` within the driver through `vxfs_extern.h`.
- Used by `vxfs_bread()`, `vxfs_getblk()`, and generic bmap/readpage paths.
