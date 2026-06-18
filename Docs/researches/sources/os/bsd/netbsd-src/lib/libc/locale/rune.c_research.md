# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/rune.c

Read completely: 430 lines.

This file loads binary rune locale data into an in-memory `_RuneLocale`. It validates the `RuneCT10` file format, converts big-endian cached tables and extended ranges, copies variable data, extracts `CODESET=`, opens the matching Citrus ctype, and builds byte-oriented ctype/toupper/tolower compatibility tables.

Important interactions: consumes structures from `runetype_file.h`, produces `_RuneLocale` from `runetype_local.h`, calls `_citrus_ctype_open`, and uses `_runetype_priv`/`_towctrans_priv` to derive byte tables. On signed-char platforms it allocates guarded ctype tables to catch negative-index ctype abuse unless compatibility mode permits it.

Security/reliability notes: validates many file-size bounds before copying range payloads, but the range arithmetic and total allocation depend on trusted counts not overflowing earlier calculations. Error paths free guarded tables and the locale object. `__mb_len_max_runtime` bounds the loaded encoding's `MB_CUR_MAX`.
