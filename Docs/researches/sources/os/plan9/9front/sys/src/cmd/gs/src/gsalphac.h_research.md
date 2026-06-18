# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.h

Purpose: Alpha-compositing public interface.

Exports: Defines `gs_composite_op_t` values matching NeXT/DPS composite operation numbering, including PostScript operators, `Highlight`, and `Dissolve`. Defines `gs_composite_alpha_params_t` with operation and dissolve delta. Declares `gs_create_composite_alpha`.

Dependencies and notes: Includes `gscompt.h`, so returned objects integrate with Ghostscript’s generic compositor abstraction.
