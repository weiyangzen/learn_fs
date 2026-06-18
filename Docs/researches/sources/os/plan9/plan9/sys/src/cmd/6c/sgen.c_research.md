# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/sgen.c

This file performs statement/tree complexity analysis and addressability rewriting for the amd64 backend.

`xcom` computes each node’s `complex` and `addable` classifications. It recognizes constants, names, registers, address-of, indirection, pointer addition, indexed addressing, shifts usable as scale factors, multiplication/division/modulo by powers of two, compound assignments, function calls, casts, comparisons, and commutable operations.

The addressability model encodes Plan 9 addressing forms: globals/statics, autos/params, constants, dereferenced constants, address constants, stack addresses, and amd64 base+index*scale addressing. `indx` extracts base, index, and scale for generated `OINDEX` nodes.

`noretval` marks no-return-value cases with NOPs targeting integer and floating return registers. `commute` and `indexshift` help canonicalize trees for cheaper code generation.

Filesystem relevance is target lowering quality. This file decides when filesystem/kernel expressions can become direct amd64 memory operands or addressing modes rather than extra instructions.
