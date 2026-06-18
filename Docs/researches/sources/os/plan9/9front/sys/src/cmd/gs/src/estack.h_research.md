# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/estack.h

## Scope

Execution-stack definitions for the Ghostscript PostScript interpreter.

## Key Behavior

- Defines cached current-file access macros and operator-visible execution stack pointers.
- Documents e-stack contents: executable procedure tails, control-flow arguments, looping state, and continuation frames.
- Provides macros for e-stack marks and pseudo-operator continuations: `make_mark_estack`, `push_mark_estack`, `make_op_estack`, and `push_op_estack`.
- Provides stack capacity/underflow checks with `check_estack` and `check_esp`.
- Declares `pop_estack`, which pops stack entries and runs cleanup procedures as needed.

## Dependencies

Includes `iestack.h` and `icstate.h`, and depends on interpreter context `i_ctx_p`, refs, ref stacks, and Ghostscript error constants.

## Risks And Invariants

- Continuation frames must keep marks and associated state together across linked-list stack blocks.
- E-stack marks are executable null refs; cleanup behavior depends on their `opproc`.
- Operators returning `o_push_estack` / `o_pop_estack` rely on exact frame layout.
