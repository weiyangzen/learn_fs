# File Research: sources/os/plan9/9front/sys/src/cmd/pic/picy.y

`picy.y` is the yacc grammar for the `pic` language. It defines tokens for drawing primitives, text, troff passthrough, control flow, attributes, positions, math functions, comparisons, and statement terminators.

The grammar turns primitive statements into generator calls (`boxgen`, `circgen`, `arcgen`, `linegen`, `movegen`, `textgen`, `troffgen`, `blockgen`), stores labels and variables, handles `copy`, `for`, `if`, `reset`, and `print`, and builds position expressions over named objects, corners, blocks, interpolation, and coordinate arithmetic.

Expressions support assignment, arithmetic, boolean comparisons, math functions, random numbers, min/max, integer truncation, and component access such as object `.x` or block variables. Attribute productions append normalized entries into the global attribute list for the generator layer.
