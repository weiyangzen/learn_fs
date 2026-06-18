# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_monetary_misc.h

Read completely: 49 lines.

This header supplies template macros for the `LC_MONETARY` category: `_CATEGORY_TYPE` as `_MonetaryLocale`, `_CATEGORY_ID` as `LC_MONETARY`, and `_CATEGORY_NAME` as `"LC_MONETARY"`. It defines an empty update hook.

Important interactions: used to instantiate the generic NetBSD locale category loader for monetary data.

Security/reliability notes: no runtime code beyond an inline no-op. The closing comment names a different guard prefix, but the actual include guard is correct.
