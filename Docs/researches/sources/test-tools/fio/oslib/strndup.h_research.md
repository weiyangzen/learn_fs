# sources/test-tools/fio/oslib/strndup.h

Purpose: declaration for fallback `strndup()`.

Important APIs/types: includes `<stddef.h>` and declares `char *strndup(const char *, size_t)` when `CONFIG_HAVE_STRNDUP` is absent.

Control flow and state: no logic or state.

Dependencies and integration: paired with `strndup.c`.

Risks: duplicate declaration risk if configure incorrectly detects libc support.

Test signals: compile matrix with native and fallback `strndup()`.
