# File Research: sources/os/linux/linux-stable/fs/vboxsf/Makefile

Builds the `vboxsf` module when `CONFIG_VBOXSF_FS` is enabled. The composite object consists of:
- `dir.o` for directory and dentry operations.
- `file.o` for regular file, symlink, address-space, mmap, and handle logic.
- `utils.o` for inode conversion, path/NLS conversion, revalidation, and directory buffering.
- `vboxsf_wrappers.o` for HGCM host-service calls.
- `super.o` for mount context, superblock, module setup, and filesystem registration.
