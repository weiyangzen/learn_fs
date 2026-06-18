# File Research: sources/os/linux/linux/fs/isofs/joliet.c

Implements Joliet Unicode filename conversion.

Key functions:
- `uni16_to_x8()` converts big-endian UTF-16 code units to a configured NLS charset, substituting `?` on conversion failure.
- `get_joliet_filename()` converts the ISO directory record name either to UTF-8 when no NLS table is loaded or through `uni16_to_x8()` otherwise. It strips trailing `;1` and trailing periods to match Windows behavior.

This file is only built with `CONFIG_JOLIET` and is used by directory iteration and lookup when Joliet is active.
