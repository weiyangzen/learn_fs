# File Research: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.c

Shannon vendor-specific nvme-cli plugin implementation.

Main commands:
- `get_additional_smart_log`: retrieves vendor log page `0xca`, parses Shannon-specific additional SMART items, and supports normal or raw binary output.
- `get_additional_feature`: wrapper around `nvme_get_features` for Shannon additional feature IDs, notably `0x02` power management.
- `set_additional_feature`: wrapper around `nvme_set_features`, optionally reading a feature payload from file/stdin.
- `shannon_id_ctrl`: delegates to generic `__id_ctrl`.

Key structures:
- `nvme_shannon_smart_log_item`: packed item with normalized value and a 6-byte raw field, with wear-level and thermal-throttle union views.
- `nvme_shannon_smart_log`: fixed array of SMART items indexed by enum values.

Notable details:
- SMART fields mirror common Intel/ScaleFlux-style additional SMART concepts: program/erase fail, wear leveling, E2E/CRC, timed workload, thermal throttle, NAND/host writes, SRAM error.
- `show_shannon_smart_log` appears to print `sram_error_count` using the normalized value from `RETRY_BUFFER_OVERFLOW` but raw value from `SRAM_ERROR_CNT`, likely a copy/paste defect.
- `get_additional_feature` allocates optional returned data but does not print `result` or payload, so it mostly validates and sends the command.
- The registered command name in the header has a typo: `set-additioal-feature`.
