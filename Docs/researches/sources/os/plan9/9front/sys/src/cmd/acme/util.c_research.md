# File Research: sources/os/plan9/9front/sys/src/cmd/acme/util.c

Utility support for Acme. It covers UTF/Rune conversion, fatal error handling, warning buffering, error window creation, small Rune/string helpers, mouse-position save/restore, checked allocation wrappers, and the heuristic for placing new windows.

Important behavior:
- `cvttorunes` converts byte buffers into Rune buffers while detecting embedded NULs.
- `errorwin`, `errorwinforwin`, `warning`, and `flushwarnings` route diagnostics into per-directory `+Errors` windows.
- `makenewwindow` chooses the active column and either uses visible blank space or splits the largest suitable window.
- Allocation helpers abort through Acme’s `error` path, so callers generally assume success.

Dependencies are Acme globals and helpers from `dat.h`/`fns.h`, including `row`, `Column`, `Window`, `Text`, buffers, and the draw/thread libraries.
