# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zgstate.c

## Purpose
Implements PostScript graphics-state allocation and operators for save/restore, line attributes, dash state, curve behavior, fill adjustment, limit clamping, and text rendering mode.

## Key Functions
- `int_gstate_alloc()` allocates and initializes Ghostscript’s interpreter graphics-state extension.
- `zgsave()`, `zgrestore()`, `zgrestoreall()`, and `zinitgraphics()` wrap whole-state operations.
- `zsetlinewidth()`, `zsetlinecap()`, `zsetlinejoin()`, `zsetmiterlimit()`, and current-state variants expose stroke parameters.
- `zsetdash()` and `zcurrentdash()` manage dash patterns.
- Extension operators manage accurate curves, curve joins, fill adjustment, dash adaptation, dot length/orientation, limit clamp, and text rendering mode.
- `gs_istate_alloc()`, `gs_istate_copy()`, and `gs_istate_free()` are client lifecycle callbacks.

## Important Behavior
- `setlinewidth` stores the absolute width to match Adobe behavior.
- Dash arrays are unpacked into temporary floats for validation, while the original array is retained in interpreter state.
- Initial black-generation and undercolor-removal procedures are executable arrays containing `pop 0.0`.
- Remap-color state is allocated in global VM so copied graphics states can live in global VM.

## Research Notes
Central bridge between PostScript operator semantics and Ghostscript graphics-state structures.
