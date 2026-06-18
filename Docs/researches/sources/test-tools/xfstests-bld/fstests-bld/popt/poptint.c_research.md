# sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.c

Purpose: internal support routines for popt: UTF-8 character stepping, gettext domain handling in UTF-8, locale conversion for formatted help output, and inclusion of the Jenkins lookup3 pair hash used by `poptBits`.

Important functions: `POPT_prev_char`, `POPT_next_char`, optional `POPT_dgettext`, optional `strdup_locale_from_utf8`, and `POPT_fprintf`. The file also maps `lookup3.c` into `poptJlu32lpair`.

Control flow: help/wrapping code calls character stepping to avoid splitting UTF-8 continuation bytes. `POPT_fprintf` formats into a dynamically allocated UTF-8 buffer, optionally converts to the current locale using iconv, then writes to the stream. `POPT_dgettext` temporarily binds a translation domain to UTF-8.

State/persistence: mostly stateless, but gettext domain codeset binding is temporarily mutated and restored. Formatted buffers and converted strings are temporary allocations.

Dependencies/integration: depends on `system.h`, `poptint.h`, `stdarg`, optional gettext/libintl, iconv, langinfo, and bundled `lookup3.c`. `popt.c` uses the hash for Bloom filters; `popthelp.c` uses formatting and character navigation.

Risks: `POPT_prev_char` assumes the caller is not at the beginning of a string and scans backward until a non-continuation byte. Locale conversion has complex error/realloc paths and may lose text on invalid input. The static `utf8_skip_data` table is present but not used by the stepping helpers.

Test signals: help wrapping under non-ASCII locales and `tdict.c`/bitset usage are the main indirect tests. Exact ASCII help tests do not fully cover iconv or multibyte behavior.
