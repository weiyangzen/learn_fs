# File Research: sources/local-fs/ntfs-3g/libntfs-3g/efs.c

## Role

Provides limited processing for NTFS encrypted files, focused on getting/setting EFS metadata and fixing raw encrypted data attributes when restoring encrypted files.

## Main Functions

- `ntfs_get_efs_info()` reads EFS information from `AT_LOGGED_UTILITY_STREAM` when the inode has `FILE_ATTR_ENCRYPTED`.
- `fixup_loop()` iterates all `AT_DATA` attributes, making them non-resident if needed, then applying EFS fixup.
- `ntfs_set_efs_info()` creates and writes the `$EFS` logged utility stream, rejects already encrypted or compressed files, validates the EFS header length, fixes data attributes, and sets inode encrypted flags.
- `ntfs_efs_fixup_attribute()` converts a raw restored encrypted data stream into NTFS encrypted-attribute form by reading the trailing padding length, truncating appended bytes, forcing non-resident state, updating sizes, and setting `ATTR_IS_ENCRYPTED`.

## Dependencies

Uses attribute, inode, directory/index, xattr, logging, and misc helpers. It shares NTFS encrypted attribute structures through `efs.h`.

## Important Behavior

Encrypted files cannot also be compressed here; the code rejects compressed inodes with `EIO`. Raw encrypted streams must have a data size congruent to 2 modulo 512, with the final two bytes encoding padding length. Invalid padding or stream shape is rejected.

Encrypted `AT_DATA` attributes must be non-resident. If normal conversion cannot make an attribute non-resident due to MFT space, the code may force non-residency and reinitialize the attribute search context.

## Research Notes

This is restore/import support rather than full EFS cryptography. It stores the EFS metadata and repairs NTFS attribute metadata so Windows-compatible encrypted file structure is represented on disk.
