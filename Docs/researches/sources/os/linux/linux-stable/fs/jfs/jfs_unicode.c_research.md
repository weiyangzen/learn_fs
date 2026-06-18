# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.c

## Role

Implements conversion between Linux dentry byte names and JFS UCS-2 style internal names.

## Main Responsibilities

- `jfs_strfromUCS_le()` converts little-endian UCS strings to byte strings:
  - Uses mounted NLS table when present.
  - Falls back to Latin-1 style byte conversion when no NLS table is present.
  - Replaces unsupported non-Latin-1 characters with `?` and limits warnings to five total occurrences.
- `jfs_strtoUCS()` converts byte strings to `wchar_t` UCS names:
  - Uses NLS `char2uni()` when available.
  - Falls back to direct byte widening without NLS.
  - Returns conversion errors from the NLS layer.
- `get_UCSname()` validates maximum name length, allocates a UCS buffer with `GFP_NOFS`, converts the dentry name using the mount NLS table, and frees on conversion failure.

## Interactions

- Uses `JFS_SBI(dentry->d_sb)->nls_tab`.
- Produces `struct component_name` values consumed by directory code.
- `free_UCSname()` is provided inline in the header.

## Correctness Notes

The conversion path is allocation-sensitive and uses `GFP_NOFS` to avoid filesystem recursion. Without `iocharset`, non-Latin-1 names are lossy.
