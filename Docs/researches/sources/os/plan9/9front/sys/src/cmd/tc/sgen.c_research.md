# File Research: sources/os/plan9/9front/sys/src/cmd/tc/sgen.c

Generates code for statements and computes addressability/complexity for expressions.

Key points:
- `codgen` emits a function prologue `TEXT`, handles the first register argument, generates the function body, warns on missing returns, emits final return code, invokes register optimization, and adjusts stack size for argument-safe space.
- `supgen` generates code in suppression mode for dead or constant-folded branches without keeping emitted instructions.
- `gen` handles statement nodes: lists, returns, labels, gotos, cases, switches, loops, continue/break, if/else, and used/set pseudo-operations.
- Switch statement generation collects cases, emits body and break target, then calls `doswit`.
- `usedset` emits `NOP` markers for volatile/set/use tracking.
- `noretval` emits pseudo uses of return registers to preserve return-value liveness.
- `xcom` computes expression addressability and register complexity, folds address/indirect patterns, normalizes constant operands, rewrites power-of-two multiplies/divides/modulos into shifts/ands, and marks function calls as high complexity.
- `bcomplex` prepares conditional expressions, performs type compatibility checks, constant-deadhead detection, 64-bit boolean lowering, and branch generation.

Dependencies and interactions:
- Calls `complex`, `cgen`, `sugen`, `doswit`, `regopt`, and many emission helpers from `txt.c`.
- Uses global control-flow labels `breakpc`, `continpc`, and `cases`.

Research relevance:
- This file is the statement-level frontend to the backend code generator.
