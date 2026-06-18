# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iht.h

Declares halftone screen helper procedures exported by `zht.c`.

Key points:
- `zscreen_params` parses screen halftone parameters into `gs_screen_halftone`.
- `zscreen_enum_init` initializes screen enumeration against a halftone order, screen params, procedure ref, operand pop count, finish proc, and VM space index.
- Used by `zht1.c` and `zht2.c`.

Research relevance:
- Shared interface for PostScript halftone/screen operator implementation.
