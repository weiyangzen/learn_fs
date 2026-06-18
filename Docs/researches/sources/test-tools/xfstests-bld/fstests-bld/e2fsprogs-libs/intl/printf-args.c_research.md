# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.c

Purpose: fetches a parsed printf argument list from a `va_list` into typed storage for later positional formatting.

Important APIs and control flow: `printf_fetchargs(va_list args, arguments *a)` iterates over `a->arg[0..count)` and dispatches on each `arg_type`. It uses default argument promotions for small integer and char types, handles optional long long, long double, wide char/string, pointer, string, and `%n` count-pointer variants, and returns `-1` for `TYPE_NONE` or unknown types.

State and persistence: no global state. It mutates caller-provided `arguments` by filling each union field.

Dependencies and integration: depends on `printf-args.h`. `vasnprintf.c` calls it after `printf_parse()` has registered all required argument types.

Risks and test signals: correctness depends on the parser assigning exactly the ABI type expected by `va_arg`; a mismatch is undefined behavior. Test every length modifier, positional reuse, `*` width/precision arguments, `%n`, disabled `HAVE_LONG_LONG`/wide-type configurations, and unknown-type rejection.
