# File Research: sources/os/plan9/9front/sys/src/cmd/va/a.y

`a.y` is the yacc grammar for MIPS assembly syntax. It parses labels, variable assignments, scheduling directives, instruction forms, registers, memory operands, branch relatives, immediates, static/extern/auto/param symbols, constants, and arithmetic/bitwise expressions.

Each instruction production emits object code through `outcode()` with `Gen` operands and optional register fields. The grammar covers integer, load/store, branch/jump, TEXT/GLOBL/DATA, floating point, coprocessor, WORD, NOP, BREAK/CACHE-overloaded, and scheduler directives.

It is architecture-specific parser glue; instruction semantics and binary encoding are downstream in object emission/linker conventions.
