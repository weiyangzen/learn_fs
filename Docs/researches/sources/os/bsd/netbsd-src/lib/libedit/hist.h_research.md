# File Research: sources/os/bsd/netbsd-src/lib/libedit/hist.h

This internal header defines libedit's history adapter state and helper macros.

Key types:
- `hist_fun_t`: callback type for history operations.
- `el_history_t`: current-line scratch buffer, buffer size, last pointer, selected event number, backend reference, backend function, and event cookie.

Key macros:
- `HIST_FUN_INTERNAL()` calls the installed history function and returns `ev.str` or NULL.
- `HIST_FUN()` routes through `hist_convert()` when `NARROW_HISTORY` is set.
- Convenience macros wrap common operations: `HIST_NEXT`, `HIST_FIRST`, `HIST_LAST`, `HIST_PREV`, `HIST_SET`, `HIST_LOAD`, `HIST_SAVE`, `HIST_SAVE_FP`, and `HIST_NSAVE_FP`.

Declared functions:
- History lifecycle, event loading, backend installation, command handling, buffer growth, and narrow-to-wide conversion.

Integration:
- Included by `el.h`; command files use these macros for history navigation/search.
