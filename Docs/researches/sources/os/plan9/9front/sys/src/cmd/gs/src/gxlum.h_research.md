# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxlum.h

Small Ghostscript luminance constants header.

Key contents:
- Defines RGB luminance weights: red 30, green 59, blue 11.
- Defines `lum_all_weights` as the total weight.

Notable dependencies:
- None beyond the surrounding C preprocessor environment.

Research notes:
- These integer weights approximate common 30/59/11 grayscale conversion behavior and are used by color/printer code elsewhere.
