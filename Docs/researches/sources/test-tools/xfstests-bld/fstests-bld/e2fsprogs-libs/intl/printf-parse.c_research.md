# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.c

Purpose: parses narrow or wide printf format strings into directive metadata and a typed argument table.

Important APIs and control flow: `PRINTF_PARSE(format, d, a)` is macro-renamed to `printf_parse` or `wprintf_parse`. It scans for `%`, records directive bounds, flags, width/precision spans, positional indices, conversion, and argument index. `REGISTER_ARG` grows `a->arg` using `xsum`/`xtimes`, initializes missing entries to `TYPE_NONE`, and rejects positional reuse with incompatible types. It supports XSI positional syntax (`n$`, `*n$`), C99 `j`, `z`/`Z`, `t`, `hh`, `h`, `l`, `ll`, `L`, and normal conversions.

State and persistence: allocates `d->dir` and `a->arg`; caller frees them. On error it frees partial allocations and returns `-1`.

Dependencies and integration: used by `vasnprintf.c` and included by `printf.c` for fallback implementations. Depends on `xsize.h` for overflow detection and `printf-args.h` for type registration.

Risks and test signals: malformed format strings, huge positional indices, and incompatible positional reuse are the key risks. Test all flags, `%`, `%n`, wide aliases `C`/`S`, width/precision positions, overflow paths, and cleanup on parse failure.
