# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nl_langinfo.c

Read completely: 196 lines.

This file implements `nl_langinfo` and `nl_langinfo_l`. Static tables map supported `nl_item` values to locale categories and byte offsets within category structs. The function returns an empty string for out-of-range or unused items, otherwise copies the pointer stored at the computed offset.

Important interactions: reads `_TimeLocale`, `_NumericLocale`, `_MessagesLocale`, and `_RuneLocale` data from `loc->part_impl`. `CODESET` is served from `_RuneLocale.rl_codeset`.

Security/reliability notes: table offsets are stored as `uint16_t`, so struct offsets must fit. It assumes each mapped offset refers to a `char *` field. Unsupported ERA/ALT_DIGITS/CRNCYSTR entries intentionally return empty strings.
