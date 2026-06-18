# File Research: sources/virtualization/nbdkit/filters/checkwrite/Makefile.am

Purpose: builds the checkwrite filter and optional manual page.

Key details:
- Builds `nbdkit-checkwrite-filter.la` from `checkwrite.c`.
- Includes common nbdkit and utility headers.
- Links `common/utils`, `common/replacements`, and Windows import support.
- Uses `filters.syms` when linker scripts are enabled.
- Generates `nbdkit-checkwrite-filter.1` from POD when available.
