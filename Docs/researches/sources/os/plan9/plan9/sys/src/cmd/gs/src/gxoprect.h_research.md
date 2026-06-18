# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxoprect.h

Public/internal interface for generic overprint rectangle fills.

Key contents:
- Declares `gx_overprint_generic_fill_rectangle` for non-separable color encodings.
- Declares `gx_overprint_sep_fill_rectangle_1` for separable encodings where depth can use fill-chunk masking.
- Declares `gx_overprint_sep_fill_rectangle_2` for separable byte-oriented cases such as 24-bit depth.
- Documents byte-swapping expectations for color and retain masks on little-endian machines.

Notable dependencies:
- Requires Ghostscript device, color index, and memory types from including context.

Research notes:
- The interface preserves implementation split by target color encoding rather than by high-level drawing operation.
