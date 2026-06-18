# File Research: sources/local-fs/squashfs-tools/squashfs-tools/date.h

Small header for `date.c`.

Exports:
- External `read_bytes(int, void *, long long)` used by `exec_date()`.

Defines:
- `TRUE` and `FALSE`.

Notable quirk:
- Does not declare `exec_date()` itself, so callers must get that prototype elsewhere or compile without strict prototype checking.
