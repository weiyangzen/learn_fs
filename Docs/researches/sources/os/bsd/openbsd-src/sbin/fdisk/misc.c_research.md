# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/misc.c

## Purpose
Shared utility functions for `fdisk`.

## Key Behavior
- Defines supported display/input units: bytes, sectors, KiB, MiB, GiB, TiB.
- `units_size()` converts sector counts into requested display units using disklabel sector size.
- `string_from_line()` reads from stdin, trims optionally, and bounds-checks copied input.
- `ask_yn()` prompts yes/no, honoring global `y_flag`.
- `getuint64()` prompts for bounded numeric values with support for:
  - default value
  - `*` as maximum
  - relative `+`/`-`
  - units `c`, `b`, `s`, `k`, `m`, `g`, `t`
- `hex_octet()` parses one-byte hex partition IDs.
- `string_to_uuid()` wraps `uuid_from_string()` while treating `uuid_s_bad_version` as acceptable.

## Notes
`getuint64()` is explicitly adapted from `disklabel/editor.c`, giving `fdisk` similar unit-aware interactive size entry.
