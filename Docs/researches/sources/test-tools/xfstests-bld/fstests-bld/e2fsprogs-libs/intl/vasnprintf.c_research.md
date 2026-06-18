# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.c

Purpose: implements dynamically sized `vasnprintf`/`vasnwprintf` with support for parsed positional printf directives.

Important APIs and control flow: `VASNPRINTF(resultbuf, lengthp, format, args)` macro-expands to narrow or wide implementation. It parses the format, fetches typed arguments, allocates a temporary directive buffer, then iterates literal spans and directives. `%%` appends a literal percent; `%n` writes the current output length; other conversions reconstruct a single-directive format string, supply optional width/precision prefixes, and call `snprintf`/`swprintf` when available or a sized `sprintf` fallback otherwise. `ENSURE_ALLOCATION` grows result storage using checked `xsize.h` arithmetic.

State and persistence: no globals. The returned buffer is either caller-provided `resultbuf` or malloc-allocated. On errors it frees internal allocations, sets `errno` to `EINVAL` or `ENOMEM`, and returns `NULL`.

Dependencies and integration: used by `printf.c` fallback wrappers and as public `vasnprintf` declarations. Depends on `printf-parse.c`, `printf-args.c`, wide-character feature macros, `snprintf`, and platform float limits.

Risks and test signals: portability logic for non-C99 `snprintf`, `%n`, wide conversions, MB_CUR_MAX sizing, and no-snprintf fallbacks is complex. Test truncation, huge widths/precisions, every conversion class, `%n`, NULL/resultbuf reuse, ENOMEM paths, and wide/narrow builds.
