# File Research: sources/os/plan9/9front/sys/src/cmd/grap/grap.h

Central header for the `grap` preprocessor. It defines error macros, input source kinds, constants for margins/frame/ticks, side and justification bitmasks, and core structs: `Infile`, `Src`, macro argument frames, `Point`, `Attr`, `Obj`, and `YYSTYPE`.

It declares all shared globals and functions across parsing, input expansion, coordinate handling, frame/label/plot/tick generation, symbol table operations, and graph output. This is the coupling point for the old yacc-based implementation.
