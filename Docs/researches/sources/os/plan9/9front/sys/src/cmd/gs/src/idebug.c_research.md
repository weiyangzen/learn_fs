# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.c

Implements debug printing and dumping helpers for interpreter refs, arrays, and stacks.

Key behavior:
- Forces `DEBUG` for this compilation unit.
- Defines type-name string table and references `tx_next_index`.
- Prints names by converting name refs or indexes to string refs.
- `debug_print_full_ref` prints detailed ref type/attributes and payload for arrays, booleans, devices, dictionaries, files, integers, names, op arrays, operators, reals, saves, strings, structs, and unknown types.
- Packed refs are decoded as executable operators, packed integers, literal names, or executable names.
- `debug_dump_one_ref` prints type, access attributes, size, raw value bits, and printable object representation when available.
- `debug_dump_refs` dumps a contiguous ref region.
- `debug_dump_stack` walks a ref stack from top to bottom.
- `debug_dump_array` handles normal, mixed, short packed, and op arrays, expanding packed elements as needed.

Research notes:
- This file is developer diagnostics only and depends on many interpreter internals.
- Struct printing assumes `gsalloc.c` object headers for type discovery.
