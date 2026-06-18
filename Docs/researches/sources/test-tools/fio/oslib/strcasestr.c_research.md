# sources/test-tools/fio/oslib/strcasestr.c

Purpose: fallback case-insensitive substring search.

Important APIs/functions: defines `strcasestr(const char *s1, const char *s2)` when `CONFIG_STRCASESTR` is absent.

Control flow and state: walks the haystack and needle, comparing exact or `tolower()` values; resets to the next haystack position on mismatch and returns the first match or `NULL`.

Dependencies and integration: paired with `strcasestr.h`; supports option and string parsing on platforms missing GNU `strcasestr()`.

Risks: passes plain `char` values to `tolower()` without casting to `unsigned char`, which is undefined for negative signed-char non-ASCII bytes. Locale behavior follows C library `tolower()`.

Test signals: empty needle, no match, case variants, overlapping patterns, and high-bit byte inputs.
