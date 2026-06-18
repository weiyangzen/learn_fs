# File Research: sources/os/bsd/netbsd-src/lib/libintl/Makefile

Build file for NetBSD `libintl`.

It builds library `intl` from gettext, textdomain, iconv conversion, dummy GNU-compat symbol, string hash, sysdep support, and plural parser sources. It installs `libintl.h` to `/usr/include` and wires `gettext.3` manual links for gettext, plural gettext, domain binding, textdomain, and codeset APIs.
