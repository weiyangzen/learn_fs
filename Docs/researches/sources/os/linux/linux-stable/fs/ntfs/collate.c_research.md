# File Research: sources/os/linux/linux-stable/fs/ntfs/collate.c

Purpose: Implements NTFS index collation rules used to compare keys in sorted metadata structures.

Supported rules:
- Binary byte collation via `ntfs_collate_binary()`.
- Single little-endian ULONG collation via `ntfs_collate_ntofs_ulong()`.
- Array of little-endian ULONGs via `ntfs_collate_ntofs_ulongs()`.
- Filename collation via `ntfs_collate_file_name()`, first case-insensitive then case-sensitive.

Public entry point:
- `ntfs_collate()` dispatches based on `COLLATION_*` rule and returns negative/zero/positive ordering or `-EINVAL` for unknown/invalid comparisons.

Important behavior:
- Binary collation compares common prefix, then shorter length sorts first.
- ULONG collation validates exact 4-byte length.
- ULONG-array collation requires equal lengths and 4-byte alignment.
- Filename collation uses the NTFS upcase table from the volume.

Risk notes:
- `ntfs_collate_ntofs_ulongs()` logs invalid lengths and returns `-1`, which can look like “less than” rather than a distinct error to callers.
- Unknown collation rules are explicitly logged and rejected.
