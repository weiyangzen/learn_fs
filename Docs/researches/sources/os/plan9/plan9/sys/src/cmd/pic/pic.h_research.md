# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/pic.h

Central header for the `pic` implementation. It defines geometry constants, style/text flags, direction encodings, the variable-sized `obj` representation, yacc semantic union, symbol table, attributes, text records, input-source stack records, file stack records, macro argument frames, and block push-stack state.

It declares the large shared global state used by parser, generators, input, and output: object/text/attribute arrays, current position, direction, codegen flag, picture extents, line/file state, and block stack.

Function declarations cover macro input, loops/conditionals, variable/symbol lookup, object generation, geometry helpers, output helpers, text saving, attribute construction, and math wrappers.

The header encodes many cross-module contracts: object `o_val` fields are type-specific, style bits combine in `o_attr`, and parser tokens from `y.tab.h` must match generator expectations.
