# File Research: sources/os/linux/linux/fs/efivarfs/file.c

Implements file operations for individual EFI variable files.

Key behavior:
- Writes expect a leading 32-bit attributes word followed by variable data.
- Rejects invalid attribute bits outside `EFI_VARIABLE_MASK`.
- Uses `efivar_entry_set_get_size()` to atomically set firmware variable data and learn the new size.
- Treats `-ENOENT` after a successful set as deletion and sets inode size to zero.
- Reads rate-limit per user, queries variable size, reads attributes plus data, and returns them as the file payload.
- Represents uncommitted newly-created variables as zero-length files returning EOF.
- Open increments `open_count`; release decrements it and removes a deleted zero-size variable dentry when the last opener closes.

Important interactions:
- Uses inode locking to serialize size and removed-state updates.
- File private data points at `struct efivar_entry`.
- Write/delete behavior is coupled to `simple_recursive_removal()` cleanup in release.
