# File Research: sources/virtualization/nbdkit/filters/delay/Makefile.am

Purpose: builds the delay injection filter and optional manual page.

Key details:
- Builds `nbdkit-delay-filter.la` from `delay.c`.
- Includes nbdkit public/generated headers.
- Links Windows import support.
- Uses filter symbol script when enabled.
- Generates `nbdkit-delay-filter.1` from POD when available.
