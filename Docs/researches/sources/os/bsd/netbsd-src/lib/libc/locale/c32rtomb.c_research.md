# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.c

Read completely: 229 lines.

This file implements `c32rtomb` and `c32rtomb_l`, converting a UTF-32 scalar value to the current locale's multibyte encoding. It rejects surrogate code points, opens a Citrus iconv converter from `utf-32le` to the locale `CODESET`, converts into a temporary buffer, decodes that as one wide character, then emits it with `wcrtomb_l` using the caller's conversion state.

Important interactions: depends on Citrus iconv internals and `nl_langinfo_l(CODESET, loc)`. It uses `le32enc`, `mbrtowc_l`, and `wcrtomb_l` as the bridge between Unicode scalar values and NetBSD's locale/wide-character machinery.

Security/reliability notes: iconv open failures are mapped to `EIO`; conversion errors propagate through `errno`. The file preserves `errno` on success. The comments flag unresolved questions about relying on iconv for surrogate rejection and combining-character behavior.
