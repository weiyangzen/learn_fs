# File Research: sources/os/bsd/netbsd-src/lib/libintl/gettext.c

Main implementation of NetBSD `libintl` gettext lookup.

Key behavior:
- Provides gettext/dgettext/dcgettext/ngettext/dngettext and context-aware pgettext variants.
- Looks up locale paths from `LANGUAGE`, `LC_ALL`, category-specific env vars, or `LANG`, with locale fallback splitting.
- Locates `.mo` files under bound textdomain directories and maps them with `mmap`.
- Validates GNU `.mo` headers, flips endian fields, builds host-order original/translation tables, optional hash tables, charset metadata, and plural parser state.
- Supports `.mo` revisions with system-dependent strings and expands sysdep records into hash lookup.
- Looks up translations through hash table first, binary search second.
- Applies plural expression results to NUL-separated plural translation strings.
- Converts translation encoding through `__gettext_iconv` unless translating the empty header string.
- Falls back to original singular/plural message on failure.

State is cached by last domain/category/language path and per-domain binding mappings.
