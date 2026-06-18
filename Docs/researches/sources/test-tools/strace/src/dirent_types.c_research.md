<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dirent_types.c -->
## sources/test-tools/strace/src/dirent_types.c

Purpose: Materializes the `dirent_types` xlat table for directory entry type names.

Important APIs and types: Includes `xlat/dirent_types.h` after `<dirent.h>`.

Control flow: No executable flow in this file.

State and persistence: Defines static/generated xlat data through the included header.

Dependencies and integration: Used by `dirent.c`, `dirent64.c`, and any decoder that prints `DT_*` values.

Risks: Depends on platform `dirent.h` constants and generated xlat content.

Test signals: Directory-entry tests should verify numeric d_type values print symbolic `DT_*` names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dirent_types.c -->
