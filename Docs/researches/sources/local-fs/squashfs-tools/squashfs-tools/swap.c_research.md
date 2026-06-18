# File Research: sources/local-fs/squashfs-tools/squashfs-tools/swap.c

This source implements the byte-swap functions declared by `squashfs_swap.h` for big-endian builds. On little-endian builds, the file compiles to no operational code because all definitions are inside `#if __BYTE_ORDER == __BIG_ENDIAN`.

Key functions:
- `swap_le16`, `swap_le32`, `swap_le64`: copy bytes from source to destination in reverse order.
- `inswap_le16`, `inswap_le32`, `inswap_le64`: return swapped scalar values.
- Macro-generated `swap_le{16,32,64}_num`: copy-swap arrays.
- Macro-generated `inswap_le{16,32,64}_num`: in-place swap arrays.

Important behavior:
- The code operates on `void *` byte pointers for copy-swap paths, so callers can pass field addresses from packed on-disk structures.
- `inswap_le64` casts input to `unsigned long long` before shifting, avoiding signed right-shift issues.

Corruption-sensitive details:
- No bounds checking occurs here; array counts must already be validated by callers.
- These helpers are only v4 endian helpers. Older v1/v2/v3 bitfield swapping is implemented by macros in `squashfs_compat.h`.
