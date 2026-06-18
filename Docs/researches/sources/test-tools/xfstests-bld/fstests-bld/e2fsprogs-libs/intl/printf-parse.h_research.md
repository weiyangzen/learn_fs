# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.h

Purpose: defines narrow-character printf directive metadata and parser API.

Important APIs/types/functions: flag macros represent grouping, left alignment, sign, space, alternate form, and zero padding. `ARG_NONE` is the sentinel for no consumed argument. `char_directive` records the source span, width/precision spans, width/precision argument indices, conversion character, and main argument index. `char_directives` holds the directive array and maximum width/precision literal lengths. It declares `printf_parse`.

State and persistence: no global state. The parser allocates `char_directives.dir`, which callers own.

Dependencies and integration: includes `printf-args.h`; consumed by `printf-parse.c`, `vasnprintf.c`, and `printf.c` fallback code.

Risks and test signals: the structure stores pointers into the original format string, so callers must keep the format alive while formatting. Test sentinel handling, literal max-length tracking, and conversion normalization for `C`/`S` in platforms that support those extensions.
