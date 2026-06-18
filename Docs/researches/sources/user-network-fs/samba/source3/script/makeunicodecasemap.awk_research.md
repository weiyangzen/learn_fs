# sources/user-network-fs/samba/source3/script/makeunicodecasemap.awk

Purpose: AWK generator for a 65,536-entry Unicode case/character-class map.

Important APIs, types, and functions: `reset_vals` initializes current output state; `print_val` emits a map entry using fields from semicolon-delimited Unicode data; `BEGIN` sets `FS=";"`; `END` fills remaining BMP code points.

Control flow: tracks expected code point `strval`. For each input row, it fills gaps with identity/no-flag entries, emits the current row with upper/lower mappings and flags for upper/lower/digit/xdigit/space, then advances. END fills to 0xffff.

State and persistence: writes generated C initializer lines to stdout; no files are written directly.

Dependencies and integration: expects UnicodeData-like input with category in `$3` and simple uppercase/lowercase mappings in `$13`/`$14`.

Risks: limited to BMP, assumes sorted input, and can loop unexpectedly if input ordering is wrong. Field-number assumptions must match the Unicode data version.

Test signals: feed a small sorted fixture with gaps, letters, digits, spaces, and final fill behavior.
