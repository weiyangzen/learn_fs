# File Research: sources/local-fs/xfsprogs/repair/attr_repair.h

## Purpose

`attr_repair.h` declares repair-local definitions used by `attr_repair.c`. It defines legacy ACL, MAC label, and capability structures/constants needed to validate root security attribute values, and it declares the `process_attributes` entry point.

## Main Contents

- POSIX ACL tag and permission constants.
- Repair-only in-core ACL structures:
  - `struct xfs_icacl_entry`
  - `struct xfs_icacl`
- IRIX MAC label structure `xfs_mac_label_t` and MSEN/MINT label type constants.
- Attribute names and sizes for `SGI_MAC_FILE` and `SGI_CAP_FILE`.
- IRIX capability structure `xfs_cap_set_t`.
- `process_attributes` prototype.

## Dependencies

The header assumes XFS/libxfs types such as `xfs_mount_t`, `xfs_ino_t`, and `struct xfs_dinode` are available from including code. It forward-declares `struct blkmap`.

## Important Invariants

- `XFS_MAC_MAX_SETS` caps combined MAC category/division lists at 250 entries.
- The ACL structures in this header are repair-local in-core representations, not kernel on-disk structures.
- `process_attributes` is the public bridge from inode processing to attribute fork validation.

## Research Notes

The header exists mainly to preserve validation knowledge for legacy root security attributes while keeping the repair entry point independent from the implementation details in `attr_repair.c`.
