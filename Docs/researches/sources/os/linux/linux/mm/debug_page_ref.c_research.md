# File Research: sources/os/linux/linux/mm/debug_page_ref.c

Defines page reference-count tracepoint wrappers. The file creates the `page_ref` tracepoints and exports both wrapper functions and tracepoint symbols for page refcount instrumentation.

Key responsibilities:
- Defines `CREATE_TRACE_POINTS` before including `trace/events/page_ref.h`.
- Implements exported wrappers for refcount set, modification, modification-and-test, modification-and-return, modification-unless, freeze, and unfreeze events.
- Each wrapper simply calls the corresponding `trace_page_ref_*` tracepoint with the supplied page and values.

Exported functions:
- `__page_ref_set()`
- `__page_ref_mod()`
- `__page_ref_mod_and_test()`
- `__page_ref_mod_and_return()`
- `__page_ref_mod_unless()`
- `__page_ref_freeze()`
- `__page_ref_unfreeze()`

Scope:
- There is no policy or state machine here; this is instrumentation plumbing used by page reference debugging.
