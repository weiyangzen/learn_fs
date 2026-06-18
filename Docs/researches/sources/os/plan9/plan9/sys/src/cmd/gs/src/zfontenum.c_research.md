# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfontenum.c

## Purpose
Exposes platform native font enumeration to PostScript as `.getnativefonts`.

## Key Functions
- `z_fontenum()` calls `gp_enumerate_fonts_init/next/free`, copies returned name/path pairs, and returns `[ [name path] ... ] true` or `false`.

## Important Behavior
- Uses non-GC memory for the temporary linked list and interpreter memory for returned PostScript strings/arrays.
- Returns `false` when native enumeration is unavailable.
- Treats null font names or paths from the platform enumerator as I/O errors.

## Research Notes
Platform-integration glue for populating Fontmap-like data from system fonts.
