# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.c

## Role

`lobject.c` implements generic helpers over Lua objects: nil sentinel, integer/log encodings, arithmetic dispatch, numeric parsing, formatted string construction, and chunk ID formatting.

## Main Responsibilities

- Defines the global immutable nil object used for invalid indexes.
- Converts integers to and from Lua's floating-point-byte encoding for table size hints.
- Computes ceiling log2 for table sizing.
- Dispatches arithmetic operations through `luai_num*` macros.
- Parses hex digits and numeric strings, rejecting NaN/Inf spellings.
- Provides a fallback C99-style hexadecimal numeric parser.
- Builds Lua strings from a restricted internal format set: `%s`, `%c`, `%d`, `%f`, `%p`, and `%%`.
- Formats source names into chunk IDs for diagnostics, handling literal sources, file sources, and string snippets.

## Integration Points

Used by lexer, parser, VM, API, debug, and table code. It relies on `lcompat_sprintf` for pointer formatting in this illumos/ZFS environment.

## Risk Notes

Numeric parsing and formatting affect compiler diagnostics and constants. The fallback hex parser uses `1 << e`, so it inherits assumptions from Lua's numeric configuration.
