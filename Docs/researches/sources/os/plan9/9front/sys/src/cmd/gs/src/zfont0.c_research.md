# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont0.c

## Purpose
Builds Type 0 composite fonts and handles composite font define/make-font adjustments.

## Key Functions
- `zbuildfont0()` validates `FMapType`, `FDepVector`, encoding data, and FMap-specific parameters before building a composite font.
- `ztype0_adjust_FDepVector()` rewrites the parent dictionary's `FDepVector` if subfonts were scaled or replaced.
- `ztype0_define_font()` wraps `gs_type0_define_font()` and updates `FDepVector` when needed.
- `ztype0_make_font()` creates transformed composite fonts and then invokes Type 0 scaling logic.
- `ensure_char_entry()` inserts or validates entries such as `EscChar`, `ShiftIn`, and `ShiftOut`.

## Important Behavior
- Enforces Type 0 inheritance rules for nested composite subfonts.
- `fmap_escape` and `fmap_double_escape` require `EscChar`; `fmap_shift` requires `ShiftIn`/`ShiftOut`; `fmap_SubsVector` validates packed substitution widths; `fmap_CMap` uses `ztype0_get_cmap()`.
- Saves and restores an existing `FID` if build failure requires backing out dictionary mutation.
- Encoding entries must be integer indices into `FDepVector`.

## Research Notes
This file ties the CMap builder in `zfcmap.c` to Ghostscript's composite font engine.
