# File Research: sources/virtualization/nbdkit/filters/exitwhen/Makefile.am

Purpose: builds the event-driven shutdown filter and optional manual page.

Key details:
- Builds `nbdkit-exitwhen-filter.la` from `exitwhen.c`.
- Includes common headers, replacements, and utilities.
- Links common utils, replacements, and Windows import support.
- Applies shared filter symbol script when enabled.
- Generates `nbdkit-exitwhen-filter.1` from POD.
