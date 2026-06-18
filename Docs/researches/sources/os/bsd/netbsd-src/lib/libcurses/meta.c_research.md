# File Research: sources/os/bsd/netbsd-src/lib/libcurses/meta.c

Implements terminal meta-mode switching: `meta` and `__restore_meta_state`.

`meta` emits `meta_on` or `meta_off` when present, updates `_cursesi_screen->meta_state`, and flushes output. It validates `win != NULL` even though the window argument is otherwise unused; `__restore_meta_state` calls `meta(NULL, state)`, so restoration depends on this validation behavior and is a point worth checking against callers.
