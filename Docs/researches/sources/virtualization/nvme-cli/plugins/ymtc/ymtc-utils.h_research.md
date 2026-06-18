# File Research: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-utils.h

Defines YMTC vendor SMART-log data structures and attribute indexes.

Key elements:
- Defines the vendor SMART log size as 4096 bytes.
- Defines per-item component sizes: 3-byte ID, 2-byte normalized value, 7-byte raw value.
- Lists YMTC external SMART attribute IDs such as program fail, erase fail, wear leveling, PCIe CRC errors, writes, reads, temperature, and power loss protection.
- Defines internal enum indexes used to address `itemArr`.
- Defines `nvme_ymtc_smart_log_item` and `nvme_ymtc_smart_log`, with padding to a 4096-byte log page.

Dependencies:
- Used by `ymtc-nvme.c` to interpret log ID `0xca`.
