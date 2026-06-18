# File Research: sources/os/plan9/9front/sys/src/9/port/print.c

Small formatting-library glue for kernel print serialization and unsupported `%e/%f/%g`.

Key responsibilities:
- Implements `_fmtlock()` and `_fmtunlock()` using a static kernel `Lock`.
- Implements `_efgfmt()` returning `-1`, disabling floating-point style formatting.

Role:
- Supplies hooks expected by the Plan 9 formatting library in kernel context.
