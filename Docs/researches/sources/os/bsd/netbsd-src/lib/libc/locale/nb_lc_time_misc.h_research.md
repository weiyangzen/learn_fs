# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_time_misc.h

Read completely: 55 lines.

This header supplies template macros for `LC_TIME`: `_CATEGORY_TYPE` as `_TimeLocale`, `_CATEGORY_ID` as `LC_TIME`, and `_CATEGORY_NAME` as `"LC_TIME"`. It also defines index conversion macros for day, month, and AM/PM `nl_langinfo` item ranges.

Important interactions: used by time locale category implementation and related table lookups.

Security/reliability notes: no standalone runtime behavior. Index macros assume valid `nl_item` values from the corresponding ranges.
