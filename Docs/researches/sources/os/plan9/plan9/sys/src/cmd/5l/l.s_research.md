# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/l.s

## Scope

Small ARM assembly syntax sample/test file.

## Contents

- Defines a `main` text symbol and exercises ARM instruction syntax accepted by the toolchain.
- Covers shifted operands, conditional instructions, MRC, CPSR/SPSR moves, SWI, SWP, MOVM, and RFE.

## Dependencies

Uses Plan 9 ARM assembler syntax and constants from the assembler/linker pipeline.

## Risks And Invariants

- This is not runtime support code; it is a compact syntax/encoding exercise.
