# File Research: sources/virtualization/nbdkit/filters/blocksize-policy/Makefile.am

Purpose: builds the `nbdkit-blocksize-policy-filter.la` module and its optional man page.

Key details:
- Sources are `policy.c` plus `include/nbdkit-filter.h`.
- Includes nbdkit public headers, generated headers, `common/include`, and `common/utils`.
- Links `common/utils/libutils.la`, `common/replacements/libcompat.la`, and Windows import support.
- Adds `filters/filters.syms` as a linker version script when `USE_LINKER_SCRIPT` is enabled.
- Generates `nbdkit-blocksize-policy-filter.1` from POD when `HAVE_POD` is available.

Integration notes:
- The build depends on common utility helpers for parsing/rounding/power-of-two support used by `policy.c`.
