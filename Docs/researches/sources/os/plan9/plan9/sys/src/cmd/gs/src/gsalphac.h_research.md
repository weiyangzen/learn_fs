# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.h

Purpose: Declares the alpha-compositing API and operation enum.

Key interfaces: `gs_composite_op_t`, `gs_composite_alpha_params_t`, and `gs_create_composite_alpha`.

Behavior: Operation values are fixed to match NeXT Display PostScript definitions; range macros identify normal composite, rectangle-only highlight, and dissolve extension limits.

Dependencies: Includes `gscompt.h` for the generic compositor type.

Risks and notes: Enum numeric compatibility is part of the interface contract, so reordering would break serialized/compositor semantics.
