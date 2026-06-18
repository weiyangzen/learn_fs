# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_numeric_misc.h

Read completely: 49 lines.

This header supplies template macros for the `LC_NUMERIC` category: `_CATEGORY_TYPE` as `_NumericLocale`, `_CATEGORY_ID` as `LC_NUMERIC`, and `_CATEGORY_NAME` as `"LC_NUMERIC"`. It defines an empty update hook.

Important interactions: used by concrete numeric locale category code with `nb_lc_template.h`.

Security/reliability notes: no standalone runtime behavior.
