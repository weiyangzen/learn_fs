# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.c

Implements line parameter operators for Ghostscript graphics state.

Key behavior:
- `gs_setlinewidth`/`gs_currentlinewidth` delegate through `gx_line_params`.
- Validates and sets line cap and join values, returning `rangecheck` for unsupported enum values.
- `gx_set_miter_limit` validates limit >= 1 and precomputes `miter_check` using half-angle formulas, with a near-2 special case.
- `gx_set_dash` validates dash arrays, handles empty patterns, rejects negative/zero-total patterns, allocates/resizes dash pattern storage, and computes initial dash index/ink/distance from offset.
- Current dash accessors return length, pattern pointer, and offset.
- Flatness is clamped to `[0.2, 100]`.
- Stroke adjust, dash adaptation, curve join, accurate curves, dot length, and dot orientation extension operators are implemented.
- `gs_setdotorientation` only accepts CTMs with axis-aligned or swapped-axis forms.

Dependencies:
- Uses graphics state internals from `gzstate.h`, line internals from `gzline.h`, matrix helpers, and memory allocation.

Research notes:
- Dash setup is the densest stateful logic in this file.
- Error handling follows Ghostscript conventions via `return_error`.
