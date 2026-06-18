# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.c

## Purpose
Implements higher-level path and drawing-color command encoding for command-list banding.

## Main Responsibilities
- Serializes fill/stroke paths into compact clist path commands.
- Tracks and writes imager-state changes needed per band.
- Serializes drawing colors and device halftones when required.
- Handles clip-path command emission.
- Implements clist device procedures for:
  - `fill_path`
  - `stroke_path`
  - `fill_parallelogram`
  - `fill_triangle`

## Key Implementation Details
- `cmd_put_drawing_color` serializes device colors with `cmd_opv_ext_put_drawing_color` and inserts halftones as needed.
- `cmd_drawing_colors_used` estimates colors touched by pure, binary halftone, colored halftone, or general colors.
- `cmd_clear_known` invalidates per-band known-state flags.
- `cmd_write_unknown` emits missing imager parameters for each band, including misc parameters, fill adjust, CTM, dash, clip path, and color space.
- Clip paths may be emitted as:
  - a rectangle
  - a serialized filled path
  - a list of rectangles
  - outer box fallback when complex clips are disabled
- `clist_fill_path` and `clist_stroke_path` compute Y coverage, update required state, emit color/logical-op state, and serialize path commands for each affected band.
- Long dash patterns fall back to default stroke rendering.
- `clist_fill_parallelogram` fast-paths rectangular parallelograms to rectangle fill; otherwise it builds a temporary path.
- `cmd_put_path` encodes paths with relative fixed-point deltas, band-Y omission of fully outside segments, implicit close handling, and compact segment opcode choices.

## Path Encoding
- Relative fixed-point operands are encoded in variable-length forms.
- Line segments are shortened to horizontal/vertical variants when possible.
- Multiple line commands can merge into compact multi-line commands.
- Curves are specialized into variants such as `hvcurveto`, `vhcurveto`, `nrcurveto`, `rncurveto`, quadratic-like shortcuts, or symmetric `scurveto`.
- Segment notes are emitted through `cmd_opv_set_misc2` when they change and are requested.

## Fallback Conditions
- Debug flag disables path-based banding.
- Explicit disable-mask bits force default fill/stroke handling.
- Too-long dash patterns fall back.
- Drawing-color serialization failures can fall back to default path rendering.

## Dependencies
- `gxclpath.h` for opcodes, known-state flags, and exported helpers.
- `gxcldev.h` for base command writing macros/procedures.
- Path and clip internals from `gzpath.h` and `gzcpath.h`.
- Drawing color, paint, stream, and serialization helpers.

## Research Notes
This file is the central high-level drawing encoder for clists. It balances compactness, per-band state caching, and safe fallback to default rendering when operations are too complex or disabled.
