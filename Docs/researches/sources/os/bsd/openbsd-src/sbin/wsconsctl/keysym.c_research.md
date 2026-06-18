# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/keysym.c

Provides key symbol name/value conversion for `wsconsctl`.

Key behavior:
- Includes generated `keysym.h`, which provides `ksym_tab_by_name`.
- Builds a second sorted table by numeric keysym on first use.
- `ksym2name()` converts numeric keysyms to names, preferring current encoding and falling back to ISO.
- `name2ksym()` converts names to numeric keysyms and supports `unknown_N` round-tripping.
- `ksymenc()` maps keyboard encoding to ISO/L2/L5/L7/KOI lookup preference.
- `ksym_upcase()` maps function-key and Latin-1 lowercase symbols to uppercase variants for parser defaults.

Filesystem/OS relevance:
- Supports human-readable serialization and parsing of kernel keyboard maps.
