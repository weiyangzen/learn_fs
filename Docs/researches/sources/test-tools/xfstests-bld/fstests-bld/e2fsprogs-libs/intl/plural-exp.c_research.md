# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.c

Purpose: extracts and initializes plural-form expressions from gettext catalog header entries.

Important APIs and control flow: `EXTRACT_PLURAL_EXPRESSION(nullentry, pluralp, npluralsp)` searches the header for `nplurals=` and `plural=`, parses `nplurals` with `strtoul` or a fallback loop, then invokes `PLURAL_PARSE` on the plural expression string. On any missing field or parse failure it falls back to `GERMANIC_PLURAL`, representing `n != 1` with two plural forms. `GERMANIC_PLURAL` is either statically initialized using C99 designated initializers or lazily initialized by `init_germanic_plural()`.

State and persistence: the fallback expression is global static process state. Successfully parsed expressions are heap-owned by the caller and freed through `FREE_EXPRESSION`.

Dependencies and integration: depends on `plural-exp.h`, `plural.c`/`plural.y` parser symbols, ctype/string/stdlib, and name remapping for glibc, libintl, or gettext tools.

Risks and test signals: it uses substring search rather than structured header parsing and does not validate `nplurals` bounds against expression results here. Test malformed headers, whitespace, very large numbers, missing semicolons, parse errors, and default English/Germanic fallback.
