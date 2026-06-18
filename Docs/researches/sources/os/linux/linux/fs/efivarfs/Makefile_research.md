# File Research: sources/os/linux/linux/fs/efivarfs/Makefile

Builds the efivarfs module.

Key behavior:
- Adds `efivarfs.o` when `CONFIG_EFIVAR_FS` is enabled.
- Links `inode.o`, `file.o`, `super.o`, and `vars.o` into the module.

Important interactions:
- Keeps all efivarfs VFS operations and EFI variable helpers in one module object.
