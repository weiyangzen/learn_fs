# sources/test-tools/fio/oslib/strlcat.h

Purpose: declaration for fallback `strlcat()`.

Important APIs/types: includes `<stddef.h>` and declares `size_t strlcat(char *, const char *, size_t)` when `CONFIG_STRLCAT` is absent.

Control flow and state: no runtime logic.

Dependencies and integration: paired with `strlcat.c`.

Risks: configuration mismatch can conflict with system declarations.

Test signals: compile on platforms with and without native `strlcat()`.
