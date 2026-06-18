# sources/test-tools/stress-ng/stress-wcs.c

## Purpose
Implements `wcs`, a libc wide-character string stressor for comparison, copy, concatenation, search, length, collation, and transform APIs.

## Important APIs, types, and functions
`stress_wcs()` is the entry point. `stress_wcs_args_t` carries buffers, lengths, libc function pointer, method name, and failure flag. `stress_wcs_method_info_t` maps method names to wrappers. `stress_wrndstr_case()` generates randomized wide strings from upper/lower alphabets that exclude `'+'`. Wrappers cover `wcscasecmp`, `wcsncasecmp`, `wcslcpy`/`wcscpy`, `wcslcat`/`wcscat`, `wcsncat`, `wcschr`, `wcsrchr`, `wcscmp`, `wcsncmp`, `wcslen`, `wcscoll`, and `wcsxfrm` as available.

## Control flow
The stressor chooses `wcs-method`, initializes buffers and metrics, generates `str1`, synchronizes, and loops regenerating `str2`, running the selected wrapper, periodically timing it, swapping source buffers, and incrementing bogo. The `all` method rotates through all real methods. At deinit it emits per-method call rates and returns failure if verification marked any check failed.

## State and persistence
State is stack string buffers, `info`, static metrics, and the static rotating index in `stress_wcs_all()`. No persistent state is written.

## Dependencies and integration points
Registered as `stress_wcs_info` with `CLASS_CPU | CLASS_CPU_CACHE | CLASS_MEMORY`, `VERIFY_OPTIONAL`, `wcs-method` option, and per-method metrics. Depends on platform wide-char headers and libc availability macros.

## Risks and edge cases
API availability and exact fallback methods vary by libc. Collation can be locale-sensitive, so checks avoid assuming order. Verification is basic and relies on generated strings being distinct and not containing `'+'`.

## Test signals
Verification failures produce `did not return expected result` messages under verify mode and return failure. Metrics report `<method> calls per sec`. Too few compiled methods yields unimplemented behavior.
