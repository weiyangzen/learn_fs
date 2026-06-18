# File Research: sources/os/linux/linux-stable/fs/adfs/Makefile
- Purpose: Builds the ADFS filesystem module/object.
- Main object: `adfs.o` is built under `CONFIG_ADFS_FS`.
- Component objects: `dir.o`, `dir_f.o`, `dir_fplus.o`, `file.o`, `inode.o`, `map.o`, and `super.o`.
- Integration: Encodes the complete ADFS implementation units: directory formats, VFS operations, block map lookup, inode handling, and mount logic.
