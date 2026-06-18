# File Research: sources/virtualization/nbdkit/filters/exportname/Makefile.am

Purpose: builds the export-name policy/description filter and optional manual page.

Key details:
- Builds `nbdkit-exportname-filter.la` from `exportname.c`.
- Includes common headers, replacements, and utils.
- Links common utils, replacements, and Windows import support.
- Uses shared filter symbol script when configured.
- Generates `nbdkit-exportname-filter.1` from POD.
