# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_block_group.c

Block group CRC16 helper for legacy ext4 group descriptor checksum support.

Key behavior:
- Defines a static 256-entry CRC16 lookup table.
- `ext4_bg_crc16` updates a CRC over an input buffer byte by byte and returns the 16-bit result.

Notable dependencies:
- Used by `ext4_fs_bg_checksum` when `EXT4_FRO_COM_GDT_CSUM` is active and metadata_csum is not used.

Research notes:
- This file contains only checksum computation; descriptor field access and checksum placement are handled in `ext4_fs.c`.
