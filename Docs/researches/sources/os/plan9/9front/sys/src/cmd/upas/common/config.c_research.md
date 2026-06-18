# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/config.c

This file defines global path defaults for the upas mail system.

Key values:
- `MAILROOT` and `SPOOL` default to `/mail`.
- Logs default to `/sys/log`.
- Libraries default to `/mail/lib`.
- Binaries default to `/bin/upas`.
- Temporary mail files default to `/mail/tmp`.
- Shell path defaults to `/bin/rc`.

Integration and risks:
- These globals are declared in `sys.h` and consumed throughout common/filterkit/upas/fs code.
- They are mutable global pointers, so local builds or tests can override them if linked accordingly.
