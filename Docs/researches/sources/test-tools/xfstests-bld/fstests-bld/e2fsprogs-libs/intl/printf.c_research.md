# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf.c

Purpose: provides libintl printf-family wrappers that support POSIX/XSI positional parameters on systems whose native printf does not.

Important APIs and control flow: when `HAVE_POSIX_PRINTF` is false, it statically includes `printf-args.c`, `printf-parse.c`, and `vasnprintf.c`, then exports `libintl_vfprintf`, `libintl_fprintf`, `libintl_vprintf`, `libintl_printf`, `libintl_vsprintf`, `libintl_sprintf`, optional snprintf/asprintf variants, and optional wide-character variants. Each wrapper delegates directly to the system function if the format lacks `$`; otherwise it formats through `libintl_vasnprintf` or `libintl_vasnwprintf`, then writes/copies the result.

State and persistence: no global state. Temporary formatted strings are heap-allocated and freed by wrappers, except returned asprintf buffers.

Dependencies and integration: depends on platform printf feature macros, stdio/string/stdlib, optional wchar support, and DLL export attributes.

Risks and test signals: fallback `vsprintf`/`vsnprintf` behavior around truncation, `%n`, and return counts is delicate. Test both `$` and non-`$` formats, truncation copies, wide output, stream write failures, and platforms with/without `snprintf`/`asprintf`.
