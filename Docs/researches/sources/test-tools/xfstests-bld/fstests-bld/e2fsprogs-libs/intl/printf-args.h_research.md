# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.h

Purpose: declares typed storage used to replay parsed printf format directives, especially for positional arguments.

Important APIs/types/functions: `arg_type` enumerates scalar, string, pointer, wide, floating, and `%n` pointer categories. `argument` stores the selected type plus a union holding the fetched value. `arguments` groups a count and dynamic `argument *` array. It declares `printf_fetchargs`.

State and persistence: no state; it defines ownership expectations for arrays allocated by `printf-parse.c` and filled by `printf-args.c`.

Dependencies and integration: includes `stddef.h`, optional `wchar.h`, and `stdarg.h`. Used by both narrow and wide printf parsers and `vasnprintf.c`.

Risks and test signals: compile-time feature macros change enum layout and union fields, so all including translation units must share the same configuration. Test ABI consistency in standalone and statically included builds, and all optional type configurations.
