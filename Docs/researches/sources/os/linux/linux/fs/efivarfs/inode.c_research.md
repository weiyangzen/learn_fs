# File Research: sources/os/linux/linux/fs/efivarfs/inode.c

Implements efivarfs inode creation, directory operations, unlink, file attributes, and setattr handling.

Key behavior:
- `efivarfs_get_inode()` creates simple inodes with mount uid/gid, timestamps, mode, and immutable flag unless the variable is removable.
- Valid efivarfs filenames must be `VariableName-GUID`.
- `create` validates filename/GUID, rejects the Linux EFI random seed variable, determines removability, creates the inode, and initializes the in-memory EFI variable name/GUID.
- `unlink` deletes the EFI variable from firmware before removing the dentry.
- Directory inode operations provide `lookup`, `unlink`, and `create`.
- File attribute get/set exposes only the immutable flag.
- `efivarfs_setattr()` intentionally copies attributes without updating `i_size`, because file size reflects firmware variable state.

Important interactions:
- Removability is controlled by the variable validation whitelist in `vars.c`.
- Non-removable variables are immutable by default.
- `i_private` points to the embedded `struct efivar_entry`.
