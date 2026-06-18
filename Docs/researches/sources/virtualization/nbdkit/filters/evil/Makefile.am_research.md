# File Research: sources/virtualization/nbdkit/filters/evil/Makefile.am

Purpose: builds the Unix-only evil data corruption filter and optional manual page.

Key details:
- Guarded by `!IS_WINDOWS`; comment says it relies on a Unix domain socket.
- Builds `nbdkit-evil-filter.la` from `evil.c`.
- Includes common headers and utility headers.
- Links common utils and Windows import support placeholder.
- Applies shared linker symbol script when enabled.
- Generates `nbdkit-evil-filter.1` from POD.
