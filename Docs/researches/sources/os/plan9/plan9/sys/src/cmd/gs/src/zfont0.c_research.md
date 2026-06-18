# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfont0.c

## Purpose
Builds Type 0 composite fonts and handles composite font define/make-font adjustments.

## Key Functions
- `zbuildfont0()` validates `FMapType`, `FDepVector`, encoding data, and FMap-specific parameters.
- `ztype0_adjust_FDepVector()` rewrites the parent dictionary's `FDepVector` if subfonts changed.
- `ztype0_define_font()` and `ztype0_make_font()` wrap Type 0 define/scale logic.
- `ensure_char_entry()` inserts or validates `EscChar`, `ShiftIn`, and `ShiftOut`.

## Important Behavior
- Enforces Type 0 inheritance rules for nested composite subfonts.
- `fmap_CMap` uses `ztype0_get_cmap()`.
- Saves and restores an existing `FID` if build failure requires backing out dictionary mutation.
- Encoding entries must be integer indices into `FDepVector`.

## Research Notes
Ties the CMap builder in `zfcmap.c` to Ghostscript's composite font engine.
