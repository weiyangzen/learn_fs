# File Research: sources/virtualization/nbdkit/filters/error/Makefile.am

Purpose: builds the error injection filter and optional manual page.

Key details:
- Builds `nbdkit-error-filter.la` from `error.c`.
- Includes common nbdkit and utility headers.
- Links common utils, replacement compatibility, and Windows import support.
- Applies shared filter symbol script when enabled.
- Generates `nbdkit-error-filter.1` from POD.
