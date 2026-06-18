# File Research: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.h

Read completely: 19 lines, 491 bytes.

Header for DWB pathname initialization. It defines `dwbinit`, where each entry either names a string pointer to replace or a fixed array to fill, plus the array length for bounded copies.

Declared API:
- `DWBinit(char *, dwbinit *)`
- `DWBhome(void)`
- `DWBprefix(char *, char *, int)`

Dependencies:
- Consumed by `dwbinit.c` and troff startup code.

Reliability notes:
- The header documents the ownership distinction: pointer values are reallocated, fixed arrays are only overwritten if there is room.
