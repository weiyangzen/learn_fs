# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_ctype.c

Locale loader for `LC_CTYPE`.

Key behavior:
- Builds path `<root>/<name>/LC_CTYPE`.
- Maps the locale file and passes it to `_rune_load`.
- On successful load, updates global libc ctype/multibyte pointers:
  - `__mb_cur_max`
  - `_ctype_tab_`
  - `_tolower_tab_`
  - `_toupper_tab_`
  - legacy `_ctype_` when enabled
- Uses NetBSD `nb_lc_template_decl.h` and `nb_lc_template.h` for locale category lifecycle boilerplate.

Unlike other locale categories in this group, `LC_CTYPE` is loaded through runetype data rather than the generic Citrus DB/fallback template.
