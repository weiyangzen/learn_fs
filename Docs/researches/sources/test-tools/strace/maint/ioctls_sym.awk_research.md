# sources/test-tools/strace/maint/ioctls_sym.awk

Purpose: parses normalized DWARF debug information for synthetic ioctl variables and emits ioctl table entries.

Important APIs/types/functions: `dirmap`, `array_get`, `dir2str`, DWARF line handlers for DIE ids, names, types, bounds/counts, and tags, plus END logic that reconstructs `_IOC` direction/type/number/size fields.

Control flow: as `readelf` output is streamed in, the awk script records DIE parent relationships and attributes. At END it finds variables named `ioc_<NAME>`, follows their type/member data for fields `d`, `n`, and `s`, groups ioctl names by encoded value, filters redundant aliases/time32/time64 variants, and prints `{ "HEADER", "NAME", DIR, NR, SIZE },`.

State and persistence behavior: in-memory associative arrays only. Exits nonzero on missing expected DWARF attributes or unknown direction values.

Dependencies and integration points: invoked by `ioctls_sym.sh` after compiling generated C that encodes ioctl macros as array sizes. It is the final symbolic extraction stage.

Risks: tightly coupled to `readelf --debug-dump=info` formatting and the synthetic struct layout produced by `ioctls_sym.sh`. Alias filtering can suppress names that are substrings of others.

Test signals: known symbolic ioctl headers should produce stable entries; failures should identify the header and missing attribute.
