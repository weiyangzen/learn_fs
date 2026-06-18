# File Research: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.h

Private header for the gettext plural parser.

Forward-declares `struct gettext_plural` and exposes:
- `_gettext_parse_plural`
- `_gettext_calculate_plural`
- `_gettext_free_plural`

Used by `gettext.c` to parse `.mo` headers and compute plural translation indexes.
