# File Research: sources/os/plan9/plan9/sys/src/cmd/6a/a.y

This yacc grammar defines amd64 Plan 9 assembly syntax for `6a`. It parses labels, symbol assignments, instructions, constants, expressions, registers, immediates, memory operands, branch targets, and special pseudo-instruction forms.

Instruction parsing is grouped by lexer token classes such as `LTYPE0` through `LTYPE4`, `LTYPED`, `LTYPET`, `LTYPEC`, `LTYPES`, `LTYPEM`, and media/SSE-specific forms. Each rule builds a `Gen2` pair and calls `outcode`, except assignments and labels, which update assembler symbols.

The grammar covers Plan 9 assembler addressing forms including `name+offset(SB)`, `name<>(SB)` for statics, stack/parameter references through `SP` and `FP`, PC-relative branch expressions, indirect calls/jumps, indexed addressing with scale checks, and constants including integer, floating, and 8-byte string constants.

Expression grammar supports arithmetic, shifts, bitwise operations, unary complement, and parenthesized expressions. The grammar enforces some amd64-specific constraints, such as index scale values and special handling for double-precision shift/move forms using segment or long registers.

Filesystem relevance is indirect: this grammar is the input language used to assemble runtime, syscall, kernel, and filesystem-adjacent Plan 9 assembly into object files.
