# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgstate.c

PostScript graphics-state operator layer. It exposes `gsave`, `grestore`, `grestoreall`, `initgraphics`, line parameter controls, dash controls, flatness, fill adjustment, curve/dot tuning, limit clamp, and text rendering mode.

The top of the file provides small adapter helpers for real, boolean, and unsigned integer state setters/getters. `int_gstate_alloc` allocates interpreter graphics state storage and initializes internal references used by the interpreter side of `gs_state`. The save/restore operators delegate to core `gs_state` routines and maintain the interpreter-side `istate` object.

`setdash` validates a dash array, converts numeric elements into a C array, rejects negative entries and all-zero patterns, then calls `gs_setdash`. Current-state operators push numbers, booleans, or arrays back to the operand stack. Non-standard controls such as accurate curves, curve join, dash adaptation, dot length/orientation, fill adjustment, and limit clamp expose Ghostscript-specific graphics controls not present in basic PostScript.
