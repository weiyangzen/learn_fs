# File Research: sources/os/linux/linux/fs/omfs/Makefile

Build glue for the OMFS filesystem module.

Key contents:
- Builds `omfs.o` when `CONFIG_OMFS_FS` is enabled.
- Links the module from `bitmap.o`, `dir.o`, `file.o`, and `inode.o`.
- No conditional subfeatures are split out; the OMFS driver is built as one small module.
