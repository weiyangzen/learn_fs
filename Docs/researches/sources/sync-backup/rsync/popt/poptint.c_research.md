# sources/sync-backup/rsync/popt/poptint.c

Purpose: Internal popt utility implementation for UTF-8 character stepping, localized formatted output, and lookup3 hash pair generation. It supports help/output code and bitset/hash users without exposing these helpers as the primary public API.

Important APIs, types, and functions: `POPT_prev_char()` and `POPT_next_char()` move over UTF-8 continuation bytes. `POPT_dgettext()` temporarily binds a text domain to UTF-8 before calling `dgettext()` when NLS support is enabled. `POPT_fprintf()` formats into a heap buffer, optionally converts from UTF-8 to the current locale, and writes to a stream. `strdup_locale_from_utf8()` is the iconv conversion helper when available. `lookup3.c` is included with `poptJlu32lpair` symbol remapping.

Control flow: `POPT_fprintf()` uses `vasprintf()` when available or a reallocating `vsnprintf()` loop otherwise. It then either calls `strdup_locale_from_utf8()` and writes converted text, or writes the formatted buffer directly. The iconv helper handles `E2BIG` by growing output, treats invalid/incomplete sequences as failure, and resets conversion state before processing.

State and persistence behavior: No long-lived mutable state is stored here. Temporary changes to `bind_textdomain_codeset()` are restored after lookup. All format/conversion buffers are heap-allocated and freed per call.

Dependencies and integration points: Depends on `system.h`, `poptint.h`, optional `langinfo.h`, `iconv`, gettext/libintl, and the bundled `lookup3.c`. `popthelp.c` relies on `POPT_fprintf()` and UTF-8 stepping for display formatting.

Risks and test signals: Risks include pointer underflow if `POPT_prev_char()` is called at the start of a string, locale conversion failures, non-C99 `vsnprintf()` behavior, and temporary gettext codeset changes in threaded contexts. Tests should exercise UTF-8 help text, non-UTF-8 locales, long formatted lines, and builds with/without iconv/NLS.
