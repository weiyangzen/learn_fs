# File Research: sources/os/linux/linux-stable/fs/freevxfs/Makefile

This Makefile wires the FreeVxFS driver into the kernel build.

Major responsibilities:
- Builds `freevxfs.o` when `CONFIG_VXFS_FS` is enabled.
- Defines the object list that composes the module/built-in driver.

Included objects:
- `vxfs_bmap.o` for logical-to-physical block mapping.
- `vxfs_fshead.o` for fileset header discovery.
- `vxfs_immed.o` for immediate-data reads.
- `vxfs_inode.o` for inode decoding and VFS inode setup.
- `vxfs_lookup.o` for directory lookup and readdir.
- `vxfs_olt.o` for Object Location Table discovery.
- `vxfs_subr.o` for shared readpage/bmap helpers.
- `vxfs_super.o` for mount, superblock, module, and cache setup.

Key invariants:
- No write-path object is present, matching the read-only driver design.
- The aggregate object is named `freevxfs.o`, while the runtime filesystem type is registered as `vxfs`.
