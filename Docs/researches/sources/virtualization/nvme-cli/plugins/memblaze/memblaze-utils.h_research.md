# File Research: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-utils.h

This header defines Memblaze SMART log constants, layouts, and debug/printing macros.

Constants:
- SMART log sizes: old 512 bytes and new 4096 bytes.
- Field sizes for new SMART items: ID, normalized value, raw value.
- External SMART attribute IDs for Intel-like/Raisin layouts.
- Internal enum indexes mapping SMART items into arrays.
- Old Memblaze item enum indexes.

Structures:
- `nvme_memblaze_smart_log_item`: packed old-format SMART item with 3-byte ID, normalized value, and raw unions for temperature, power, thermal throttle, wear-leveling, power-loss protection, and related forms.
- `nvme_memblaze_smart_log`: old-format SMART log array plus padding to 512 bytes.
- `nvme_p4_smart_log_item`: newer Intel-like item with 3-byte ID, 2-byte normalized value, and 7-byte raw value.
- `nvme_p4_smart_log`: newer 4096-byte SMART log layout.

Macros:
- Debug macros prefixed `D...` for printing file/line/function and values.
- `fPRINT_PARAM1`/`fPRINT_PARAM2` write to a file and/or stdout depending on `fdi` and `print`.

Role:
- Provides the binary layout and attribute IDs used by both legacy and newer Memblaze SMART parsing in `memblaze-nvme.c`.
