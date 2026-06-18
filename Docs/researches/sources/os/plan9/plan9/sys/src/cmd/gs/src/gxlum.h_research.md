# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxlum.h

Small Ghostscript luminance constants header.

Key contents:
- Defines RGB luminance weights: red 30, green 59, blue 11.
- Defines `lum_all_weights` as the sum of those weights.

Notable dependencies:
- None beyond normal C preprocessing context.

Research notes:
- These integer weights approximate the common 30/59/11 grayscale conversion convention and are used by color/printer code elsewhere.
