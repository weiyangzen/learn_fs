# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.c

## Role

Implementation of FunctionType 4 PostScript Calculator functions.

## Main Data

Defines `gs_function_PtCr_t`, a calculator stack value type supporting bool/int/float, a maximum stack depth of 100, typed opcode variants, and an opcode dispatch table that maps explicit opcodes plus operand types to executable operations or coercions.

## Control Flow

Initialization validates generic parameters, stack limits, and bytecode structure through the terminating `PtCr_return`. Evaluation seeds the operand stack with inputs, interprets typed bytecode, performs arithmetic/comparison/stack/control operations, enforces stack bounds and type checks, and extracts numeric outputs. Symbolic reconstruction routines pretty-print bytecode as PostScript-like `{ ... }` text through a DataSource hack for PDF embedding. Scaled-copy creation appends multiply/add/roll operations to map outputs into requested ranges.

## Dependencies

Uses math wrappers, data-source support, Ghostscript function common helpers, streams, SubFileDecode filter, and pretty-printer streams.

## Notes

Monotonicity is intentionally unknown and returns a mask marking all dimensions uncertain. Calculator bytecode constants store native `int` and `float` representations.
