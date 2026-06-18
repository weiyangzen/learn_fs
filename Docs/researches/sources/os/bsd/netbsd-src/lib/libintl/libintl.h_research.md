# File Research: sources/os/bsd/netbsd-src/lib/libintl/libintl.h

Public `libintl` header.

Declares gettext, domain-specific gettext, plural gettext, context-aware pgettext variants, `textdomain`, `bindtextdomain`, and `bind_textdomain_codeset`. It also defines expression macros for pgettext-style helpers unless included through GNU gettext’s compatibility header.

Uses NetBSD `__format_arg` annotations to preserve format-string checking through translated strings.
