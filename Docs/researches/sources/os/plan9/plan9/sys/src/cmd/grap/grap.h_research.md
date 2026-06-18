# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/grap.h

This is the central `grap` header. It defines error macros, input-source flags, constants for margins/ticks/sides/justification, `Infile`, `Src`, `Arg`, `Point`, `Attr`, `Obj`, and `YYSTYPE`.

It declares global parser/runtime state such as object lists, current coordinate names, numeric lists, tick state, temp file, and codegen flags.

It also declares the cross-module API for coordinate handling, object/attribute management, input stack and macro processing, labels, plotting, graph finalization, and tick/grid generation.
