# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/prevy.tab.h

Checked-in yacc token header snapshot for `pic`. It defines token constants for object types, control constructs, attributes, positions, math functions, drawing styles, and operators.

The first object token values are deliberately fixed to match object type values used throughout the generator and printer code: `BOX` through `PLACE`.

The makefile updates this file from generated `y.tab.h` only when token definitions change, giving non-yacc C files a stable include.
