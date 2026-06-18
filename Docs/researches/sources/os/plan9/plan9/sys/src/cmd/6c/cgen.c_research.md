# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/cgen.c

This is the core amd64 expression code generator for `6c`. `cgen` lowers C expression trees into Plan 9 amd64 instructions, handling assignments, arithmetic, shifts, multiply/divide/modulo, address generation, function calls, indirection, comparisons, logical expressions, casts, conditionals, comma expressions, struct/union expressions, and pre/post increment or decrement.

It pays close attention to evaluation order and register pressure. If both sides of an expression can call functions, it spills one side into temporaries before continuing. It uses fixed amd64 registers where required, especially `CX` for variable shifts and `AX`/`DX` for multiply/divide.

The file delegates optimized constant arithmetic to `mulgen`, `sdivgen`, `udivgen`, `sdiv2`, and `smod2`. It has special handling for bitfields through `bitload` and `bitstore`, boolean generation through `boolgen`, and structure copying/return through `sugen`.

`lcgen` and `reglcgen` generate l-values and addresses. Helpers classify immediate constants, hard constants, useful cast folding, 64-bit high/low halves, and suspicious 32-bit masks used against 64-bit values.

Filesystem relevance is build-pipeline level: this backend emits the machine code for Plan 9 amd64 C code, including kernel and filesystem components.
