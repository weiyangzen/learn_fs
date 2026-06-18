# File Research: sources/local-fs/dlm/dlm_sand/crc32c.c

This file implements table-driven CRC-32C.

Key contents:
- A static 256-entry CRC-32C table for reflected input/output using polynomial `0x1EDC6F41`.
- Public function `uint32_t crc32c(uint32_t crc, uint8_t *data, size_t length)`.

Behavior:
- Iterates byte by byte.
- Updates `crc` as `crc32c_table[(crc ^ *data++) & 0xFF] ^ (crc >> 8)`.
- Returns the final crc accumulator.

Origin:
- Comments say it was copied from btrfs-progs, which copied from the kernel `lib/libcrc32c.c`.

Likely use:
- Included in the `dlm_sand` binary and presumably used by `ondisk.c` or related sanlock/on-disk metadata code outside this group.
