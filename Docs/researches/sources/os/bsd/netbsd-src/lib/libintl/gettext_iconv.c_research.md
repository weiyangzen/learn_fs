# File Research: sources/os/bsd/netbsd-src/lib/libintl/gettext_iconv.c

Implements translation charset conversion for gettext results.

`__gettext_iconv` compares the `.mo` charset against the bound codeset or current locale `CODESET`. If conversion is needed, it uses `iconv_open`, `iconv`, and a static allocation arena. Converted messages are cached by original message pointer in a `tsearch` tree.

Important constraints:
- Returned converted buffers are intentionally never freed due to gettext API lifetime expectations.
- Cache key compares original message pointers, not string contents.
- Locking is marked as TODO with `XXX LOCK` comments.
