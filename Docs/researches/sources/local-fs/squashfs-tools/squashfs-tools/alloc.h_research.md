# File Research: sources/local-fs/squashfs-tools/squashfs-tools/alloc.h

Small allocation wrapper header.

Provides inline wrappers:
- `_calloc`, `_malloc`, `_realloc`
- `_strdup`, `_strndup`
- `_vasprintf`, `_asprintf`

Macros pass `__func__` into each wrapper:
- `CALLOC`, `MALLOC`, `REALLOC`, `STRDUP`, `STRNDUP`, `VASPRINTF`, `ASPRINTF`.

Behavior:
- Any allocation or formatting allocation failure calls `MEM_ERROR(func)`, which logs, performs pre-exit cleanup, and exits.
- Reexports `TRUE` and `FALSE` constants.

Key role: centralizes fail-fast allocation handling across SquashFS tools.
