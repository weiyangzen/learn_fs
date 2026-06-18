# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/adosfs.h

## Summary
Defines public mount arguments and kernel-private ADOSFS data structures, constants, macros, and prototypes.

## Main Responsibilities
- Define `struct adosfs_args` for mount parameters: device path, uid, gid, and permission mask.
- Define AmigaDOS timestamp structure and `enum anode_type`.
- Define `struct anode` for root, directory, file, link, and extension block metadata.
- Define `struct adosfsmount` for per-mount geometry, ownership, device, root, and bitmap state.
- Define AmigaDOS block type constants, data offsets, and filesystem variant macros.
- Declare utility functions and vnode operations.

## Integration Notes
`anode` embeds `genfs_node` and backs vnodes through `VTOA()`/`ATOV()`. Directory nodes use `tab`/`tabi` for hash buckets and scan metadata.

## Risks
Many fields map directly to big-endian on-disk block words. Correct block-size and `nwords` derivation are critical for every table-size macro.
