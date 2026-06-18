# sources/test-tools/fio/oslib/strndup.c

Purpose: fallback `strndup()` implementation.

Important APIs/functions: allocates `n + 1` bytes, copies up to `n` bytes with `strncpy()`, and forces a trailing NUL.

Control flow and state: no persistent state; returns allocated string or `NULL`.

Dependencies and integration: paired with `strndup.h`; used where bounded string duplication is needed on platforms lacking libc support.

Risks: always allocates `n + 1`, even when source is shorter; very large `n` can overflow `n + 1`. Callers own the returned allocation.

Test signals: shorter source, exactly `n`, longer source, `n = 0`, allocation failure.
