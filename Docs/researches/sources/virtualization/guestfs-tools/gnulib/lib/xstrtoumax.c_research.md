# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoumax.c

`uintmax_t` instantiation of `xstrtol.c`.

Macro setup:
- `__strtol` = `strtoumax`
- `__strtol_t` = `uintmax_t`
- `__xstrtol` = `xstrtoumax`
- min/max = `0` / `UINTMAX_MAX`

Research relevance: generated parser variant used by human-readable block-size parsing.
