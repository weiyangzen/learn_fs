# File Research: sources/os/linux/linux/fs/ntfs/collate.c

Implements NTFS index collation rules used when comparing index keys.

Key entry points:
- `ntfs_collate()` dispatches by collation rule.
- Internal comparators handle binary data, single little-endian ULONGs, arrays of little-endian ULONGs, and file-name keys.

Core mechanics:
- Binary collation compares shared prefix with `memcmp()` and breaks ties by length.
- `COLLATION_NTOFS_ULONG` requires both inputs to be exactly 4 bytes and compares decoded little-endian values.
- `COLLATION_NTOFS_ULONGS` requires equal lengths and 4-byte alignment, then compares decoded `__le32` values in order.
- File-name collation first compares with `IGNORE_CASE` using the volume upcase table, then breaks equal folded names with a case-sensitive comparison.
- Unknown collation rules log an NTFS error and return `-EINVAL`.

Important invariants:
- `ntfs_collate()` returns negative, zero, or positive ordering values, but some error paths use `-EINVAL` or `-1`.
- File-name collation depends on `vol->upcase` and `vol->upcase_len`.

Notable risks:
- `ntfs_collate_ntofs_ulongs()` returns `-1` for invalid lengths after logging, which is indistinguishable from "less than" to callers that do not separately validate.
