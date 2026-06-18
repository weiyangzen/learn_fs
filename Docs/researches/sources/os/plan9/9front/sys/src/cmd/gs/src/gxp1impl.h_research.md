# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1impl.h

PatternType 1 implementation interface.

Key contents:
- Declares fill rectangle procedures implemented in `gxp1fill.c` for colored patterns and masked pure/binary/colored device colors.
- Declares Pattern color mapping procedures exported by `gxpcmap.c`: `gx_pattern_load` and `gs_pattern1_remap_color`.

Notable dependencies:
- Requires Pattern color definitions from `gxpcolor.h`.

Research notes:
- Uses shortened `masked_fill_rect` naming to stay within historical 32-character identifier limits.
