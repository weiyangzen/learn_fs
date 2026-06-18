# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.h

Purpose: Defines PostScript wrapper text fragments used by `ps_include.c`.

Key contents:
- `PS_head` starts inclusion, saves context, disables page operators, sets up dictionary and stack preservation.
- `PS_setup` computes bounding boxes, transforms, scale factors, clipping, whiteout, rotation, and inclusion graphics state.
- `PS_tail` restores state, optionally draws an outline, restores operand stack and context, and ends inclusion.

Dependencies and integration:
- Included directly by `ps_include.c`.
- The generated PostScript expects variables emitted by `ps_include`.

Risks and notes:
- This header contains static data definitions rather than declarations, so it is meant for single inclusion.
- Wrapper correctness depends on PostScript interpreter behavior and DSC scanning from `ps_include.c`.
