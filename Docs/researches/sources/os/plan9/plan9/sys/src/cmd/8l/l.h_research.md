# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/l.h

Purpose: central 386 linker header.

Key behavior: declares core structs `Adr`, `Prog`, `Sym`, `Auto`, `Optab`; symbol classes; operand classes; instruction encoding forms; global linker state; output-buffer macro `cput`; and function prototypes across all linker passes.

Integration notes: defines the contracts among object loading, pass/layout, span/encoding, listing, and final assembly. Any structural change affects nearly every `8l` file and the Plan 9 object format.
