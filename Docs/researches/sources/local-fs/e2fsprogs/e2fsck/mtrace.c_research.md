# File Research: sources/local-fs/e2fsprogs/e2fsck/mtrace.c

## Purpose
Legacy malloc tracing hooks adapted from GNU malloc debugging support.

## Main Behavior
- Reads `MALLOC_TRACE` environment variable.
- Opens trace stream or `/dev/null` if only `mallwatch` is set.
- Installs `__malloc_hook`, `__free_hook`, and `__realloc_hook`.
- Emits trace records:
  - `+ ptr size` on malloc,
  - `- ptr` on free,
  - `< old` and `> new size` on successful realloc,
  - `! old size` on failed realloc.
- `mallwatch` can trigger `tr_break()` when a watched pointer is allocated/reallocated/freed.
- `malloc_get_mallstream()` exposes the trace stream.

## Integration
Optional debugging module controlled by `MTRACE` settings in `Makefile.in`; paired with `mtrace.awk`.

## Risks / Notes
Uses old GNU malloc hook APIs, which are obsolete/removed in newer libc environments. This is debugging-only code and not part of normal builds unless enabled.
