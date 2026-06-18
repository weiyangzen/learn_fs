# sources/test-tools/fio/oslib/strsep.h

Purpose: declaration for fallback `strsep()`.

Important APIs/types: declares `char *strsep(char **, const char *)` when `CONFIG_STRSEP` is absent.

Control flow and state: no runtime logic.

Dependencies and integration: paired with `strsep.c`.

Risks: configuration mismatch can collide with libc declarations.

Test signals: compile on platforms with and without native `strsep()`.
