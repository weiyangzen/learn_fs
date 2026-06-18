# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regexec.c

Public `regexec()` wrapper and engine generator. It includes `engine.c` three times with different macro sets:
- small state bitset matcher for regexes fitting in a machine `long`,
- large byte-array state matcher,
- multibyte-aware matcher.

`regexec()` validates magic values, filters execution flags, and dispatches to `mmatcher()` when `MB_CUR_MAX > 1`, otherwise to `smatcher()` when state count fits and `REG_LARGE` is not requested, else to `lmatcher()`.

It provides `xmbrtowc()` wrappers that treat invalid multibyte sequences as one dummy character for matching progress, resetting conversion state after errors.
