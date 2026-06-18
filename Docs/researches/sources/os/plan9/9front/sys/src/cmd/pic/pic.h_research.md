# File Research: sources/os/plan9/9front/sys/src/cmd/pic/pic.h

`pic.h` is the shared interface for the `pic` implementation. It defines geometry constants, default dimensions, object attributes, text flags, direction encodings, source-stack types, symbol-table structures, parser value union, `obj`, `Attr`, `Text`, `Src`, `Infile`, and block push-stack state.

It also declares the global parser/output state and all cross-file functions used by the grammar, generators, symbol table, input stack, output backend, and math wrappers. The variable-length `obj` representation stores core coordinates plus an `o_val[]` payload whose meaning depends on object type.
