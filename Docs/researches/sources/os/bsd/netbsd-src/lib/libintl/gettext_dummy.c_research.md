# File Research: sources/os/bsd/netbsd-src/lib/libintl/gettext_dummy.c

Provides the global symbol `_nl_msg_cat_cntr`.

The comment explains this is a compatibility hack for GNU gettext’s autoconf macro checks, causing software to treat NetBSD `libintl` sufficiently like GNU gettext so `.mo` files install under `/usr/share/locale` rather than `/usr/lib/locale`.
