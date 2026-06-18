# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-utils.c

Implements Western Digital plugin utility routines used by WDC-specific nvme-cli commands.

Key elements:
- Wraps `vsnprintf` as `wdc_UtilsSnprintf`.
- Provides string utilities for deleting a character, case-insensitive compare, and fixed-width string formatting with trailing-space trimming.
- Provides local time extraction into `UtilsTimeInfo`, including timezone handling via `tm_gmtoff` when available or `timezone` fallback.
- Creates directories with WDC-specific status code mapping.
- Appends buffers to files with explicit partial-write status handling.
- Checks controller UUID-list support by running Identify Controller, checking `NVME_CTRL_CTRATT_UUID_LIST`, and retrieving the UUID list.

Dependencies:
- Uses libnvme identify helpers, nvme-cli status/error display helpers, and WDC status constants from `wdc-utils.h`.

Notes:
- `mkdir(path, 0x999)` is unusual permission syntax and depends on normal mode masking; it is preserved upstream behavior.
- `wdc_UtilsStrCompare` compares with `toupper` but subtracts original characters, so ordering is not fully case-folded even though equality is case-insensitive.
