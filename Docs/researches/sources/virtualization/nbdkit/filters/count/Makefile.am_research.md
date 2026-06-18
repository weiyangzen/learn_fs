# File Research: sources/virtualization/nbdkit/filters/count/Makefile.am

Purpose: builds the count filter and optional manual page.

Key details:
- Builds `nbdkit-count-filter.la` from `count.c`.
- Includes nbdkit public/generated headers.
- Links Windows import support; no extra common utility libraries are required.
- Uses the common filter symbol script when configured.
- Generates `nbdkit-count-filter.1` from POD when available.
