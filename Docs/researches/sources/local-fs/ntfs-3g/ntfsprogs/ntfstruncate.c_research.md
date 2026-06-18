# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfstruncate.c

## File Role

`ntfstruncate.c` implements the `ntfstruncate` command. It opens an NTFS volume, opens a specified MFT inode and attribute, and calls `ntfs_attr_truncate()` to resize that attribute.

Despite the man page describing a file path, this source expects:

`ntfstruncate [options] device inode [attr-type [attr-name]] new-length`

The default attribute is unnamed `$DATA`.

## Major Dependencies

The utility uses libntfs-3g primitives and layout definitions:

- `ntfs_check_if_mounted`, `ntfs_mount`, `ntfs_umount`
- `ntfs_inode_open`, `ntfs_inode_close`
- `ntfs_attr_open`, `ntfs_attr_close`, `ntfs_attr_truncate`
- `ntfs_mbstoucs`, `ntfs_ucsfree`
- `attrdef_ntfs3x_array` for attribute-name display in verbose MFT dumps
- NTFS layout structs such as `MFT_RECORD`, `ATTR_RECORD`, `VOLUME_INFORMATION`, and `ATTR_DEF`

The Makefile builds it from `attrdef.c`, `ntfstruncate.c`, `utils.c`, and `utils.h`.

## Global State

The file keeps command and resource state globally so `ntfstruncate_exit()` can clean up on error:

- `dev_name`, `inode`, `attr_type`, `attr_name`, `attr_name_len`, `new_len`
- `vol`, `ni`, `na`
- `attr_defs`
- `success`
- `opts` containing `no_action`, `quiet`, `verbose`, and `force`

## Option Parsing

`parse_options()` handles short options only:

- `-f`: force
- `-n`: no-action/read-only mode
- `-q`: quiet
- `-v`: verbose; `-vv` enables debug/trace logging
- `-V`: version
- `-l`: license
- `-h`/`-?`: usage

It validates the inode as a nonzero integer, optional attribute type as a nonzero integer, optional attribute name through `ntfs_mbstoucs()`, and new length as a non-negative plain integer. It does not implement the suffix parsing documented in the man page.

## Debug Dump Helpers

When `-vv` is active, the program dumps the MFT record before and after truncation:

- `dump_mft_record()` prints MFT header metadata and iterates attributes.
- `dump_attr_record()` prints type, length, residency, name, flags, and instance.
- `dump_resident_attr()` and `dump_non_resident_attr()` print resident/nonresident details.
- `dump_resident_attr_val()` decodes a small subset of resident values, notably `$VOLUME_NAME` and `$VOLUME_INFORMATION`; many attribute types are explicitly TODO.
- `dump_mapping_pairs_array()` is a placeholder TODO.

These dumps are diagnostic only; truncation itself is entirely delegated to libntfs-3g.

## Main Flow

`main()`:

1. Initializes logging and default NTFS 3.x attribute definitions.
2. Parses CLI arguments.
3. Sets locale.
4. Checks whether the volume is mounted and refuses unless `-f` is set.
5. Mounts read-only for `--no-action`, otherwise read-write.
6. Registers `ntfstruncate_exit()` for cleanup.
7. Opens the target inode and attribute.
8. Optionally dumps the MFT record.
9. Calls `ntfs_attr_truncate(na, new_len)`.
10. Optionally dumps the MFT record again.
11. Closes the attribute and inode, unmounts, frees the attribute name, and marks `success`.

## Safety and Risks

- Mounted-volume protection exists, but `-f` bypasses it.
- `--no-action` only switches the volume mount to read-only; the code still calls `ntfs_attr_truncate()`, relying on lower layers/read-only mount behavior to prevent writes.
- The target is an inode number, so users need precise metadata knowledge.
- Attribute diagnostics are incomplete and some display functions have TODO placeholders.
- Cleanup is centralized and avoids leaking open volume/inode/attribute handles after failures.
