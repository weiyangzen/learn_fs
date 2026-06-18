# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.c

This file implements helpers for mapping protocol/config constants between names and numeric values.

Key responsibilities:
- Look up numeric values by case-insensitive string name.
- Look up names by numeric value.
- Look up a linked map by numeric value.
- Produce fallback printable names for unknown values.
- Search multiple maps for a name.

Important functions:
- `constant_value()`
- `constant_lookup()`
- `constant_link_lookup()`
- `constant_name()`
- `constant_name_maps()`

Notable behavior:
- Unknown names map to `0`.
- Unknown values are formatted into static buffers as `<Unknown N>`.
- `constant_name()` and `constant_name_maps()` use static storage, so callers must treat returned unknown strings as transient.

Dependencies:
- `struct constant_map` from `constants.h`.

Research notes:
- This utility underpins config and protocol debugging where generated constant maps are used.
