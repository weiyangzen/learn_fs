# File Research: sources/os/linux/linux/fs/qnx6/dir.c

## Role

Implements QNX6 directory iteration and name lookup support, including long filename records stored in the filesystem longfile.

## Directory Iteration

- `qnx6_readdir()` walks directory folios and fixed-size directory entries.
- Short names are emitted directly from `de_fname`.
- Long names are detected by `de_size > QNX6_SHORT_NAME_MAX` and resolved through `qnx6_dir_longfilename()`.
- `qnx6_dir_longfilename()` reads the long filename record, validates maximum length, optionally checks checksum, and emits the long name.

## Lookup Helpers

- `qnx6_find_ino()` scans directory pages for a name, starting from cached `i_dir_start_lookup`.
- `qnx6_match()` handles short names.
- `qnx6_long_match()` loads and compares long filename records.
- `qnx6_lfile_checksum()` computes the long filename checksum used by non-MMI filesystems.

## Operations

- `qnx6_dir_operations`: generic llseek/read, `iterate_shared`, simple fsync, generic setlease.
- `qnx6_dir_inode_operations`: lookup through `qnx6_lookup`.

## Research Notes

Long filenames are indirected through a separate private longfile inode. The `mmi_fs` mount option disables checksum enforcement for long names.
