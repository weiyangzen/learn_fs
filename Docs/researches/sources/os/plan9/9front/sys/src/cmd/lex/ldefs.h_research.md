# File Research: sources/os/plan9/9front/sys/src/cmd/lex/ldefs.h

`ldefs.h` is the central definition header for the Plan 9 `lex` implementation. It defines scanner constants, array sizing defaults, regex parse-tree node codes, section markers, debug switches, and external declarations for all global compiler state.

It also declares the major functions spanning parsing, action copying, parse-tree construction, follow-position computation, DFA generation, transition packing, output layout, diagnostics, and generated header emission.

The codebase relies heavily on shared globals rather than encapsulated structs; this header is the integration contract across `lmain.c`, `parser.y`, `sub1.c`, `sub2.c`, and `header.c`.
