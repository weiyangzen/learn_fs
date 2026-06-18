# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ostack.h

Ghostscript operand stack helper header.

It maps the current interpreter context’s operand stack into short names and defines stack manipulation macros:

- `iop_stack`, `o_stack`, `osbot`, `osp`, and `ostop`.
- `check_ostack(n)` for overflow preflight.
- `push(n)` for pushing and updating `osp`.
- `pop(n)` for decrementing `osp`.
- `check_op(nargs)` for explicit stack-underflow checks.

The comments describe Ghostscript’s operand stack guard-entry scheme: the interpreter does not precheck underflow for every operator, so invalid guard refs below the stack bottom let type checks later report `stackunderflow`. It also notes that the operand stack is a linked list of blocks, so whole-stack operations must account for block boundaries.

This is interpreter stack infrastructure, not filesystem code.
