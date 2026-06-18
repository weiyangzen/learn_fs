# File Research: sources/os/linux/linux/fs/efivarfs/internal.h

Declares efivarfs private types and helper interfaces.

Key behavior:
- Defines mount options containing uid and gid.
- Defines superblock private state with mount options, superblock pointer, and EFI ops notifier.
- Defines EFI variable identity as UTF-16 name plus vendor GUID.
- Defines `struct efivar_entry`, embedding a VFS inode plus open count and removed flag.
- Provides `efivar_entry()` container helper.
- Declares variable enumeration, get, set/get-size, delete, validation, name conversion, removability, and presence-check helpers.
- Exposes efivarfs file operations, directory inode operations, and inode allocation helper.

Important interactions:
- Shared contract between `file.c`, `inode.c`, `super.c`, and `vars.c`.
- Separates firmware variable identity from VFS inode state.
