# File Research: sources/os/linux/linux-stable/fs/efivarfs/file.c

## Summary
Implements regular-file operations for EFI variables exposed through efivarfs.

## Main Responsibilities
- Reads EFI variable attributes plus data.
- Writes attributes plus data to firmware.
- Tracks open counts and deferred removal.
- Removes dentries after deletion once all opens close.

## Key APIs
- `efivarfs_file_operations`

## Important Behavior
Writes require at least a 32-bit attribute word and reject unknown attribute bits. After a successful set, the file size is updated to attributes plus firmware-reported data size. If firmware reports `ENOENT`, size becomes zero and release removes the file.

Reads rate-limit callers through the user ratelimit state, query variable size first, then return attributes followed by data.

## Risks
Writes call firmware runtime services under inode serialization. Zero-size files represent uncommitted or deleted variables, so users of `i_size` must preserve that meaning.
