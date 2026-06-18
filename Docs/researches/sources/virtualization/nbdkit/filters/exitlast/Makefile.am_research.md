# File Research: sources/virtualization/nbdkit/filters/exitlast/Makefile.am

Purpose: builds the exit-on-last-client filter and optional manual page.

Key details:
- Builds `nbdkit-exitlast-filter.la` from `exitlast.c`.
- Includes nbdkit public/generated headers.
- Links Windows import support.
- Uses shared filter symbol script when configured.
- Generates `nbdkit-exitlast-filter.1` from POD.
