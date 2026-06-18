# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.h

## Purpose

Public header for histogram counting utilities used by FSE/HUF compression.

## Main Components

- `HIST_count`
- `HIST_isError`
- `HIST_WKSP_SIZE_U32`
- `HIST_WKSP_SIZE`
- `HIST_count_wksp`
- `HIST_countFast`
- `HIST_countFast_wksp`
- `HIST_count_simple`

## API Semantics

- `HIST_count` and workspace variants update `*maxSymbolValuePtr` to the highest observed symbol.
- Return value is the largest symbol frequency, or an error code for checked/workspace variants.
- `HIST_countFast` and `HIST_count_simple` trust that source bytes are no larger than `*maxSymbolValuePtr`.

## Dependencies

- `<stddef.h>`

## Research Notes

- Workspace is caller-owned, writable, 4-byte aligned, and must be at least `HIST_WKSP_SIZE`.
- Unsafe variants are performance helpers and should only be used when byte range is already guaranteed.
