# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.c

## Purpose

Byte histogram implementation used by FSE and HUF compression to count symbol frequencies and identify the most common symbol.

## Main Components

- Error wrapper:
  - `HIST_isError`
- Counting APIs:
  - `HIST_count_simple`
  - `HIST_countFast_wksp`
  - `HIST_countFast`
  - `HIST_count_wksp`
  - `HIST_count`
- Internal parallel counter:
  - `HIST_count_parallel_wksp`
- Input-check mode:
  - `trustInput`
  - `checkMaxSymbolValue`

## Behavior

- `HIST_count_simple` zeroes `count`, scans byte-by-byte, trims `maxSymbolValuePtr`, and returns the largest frequency.
- Larger inputs use four 256-entry counters updated in stripes from 32-bit loads, then recombined.
- Checked mode validates that no symbol exceeds the requested maximum.
- Workspace must be 4-byte aligned and at least `HIST_WKSP_SIZE`.

## Dependencies

- `mem.h`
- `debug.h`
- `error_private.h`
- `hist.h`

## Research Notes

- The threshold for simple counting is `sourceSize < 1500`.
- `HIST_countFast` trusts input range and can write out of bounds if called with a too-small max symbol value.
- The max-symbol trimming loop assumes at least one counted symbol when source size is nonzero.
