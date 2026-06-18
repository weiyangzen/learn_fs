# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstack.c

## Purpose
Implements Ghostscript operand-stack PostScript operators: stack manipulation, marks, counts, and roll/index behavior.

## Public Surface
- `zpop`, `zexch`, `zdup`, `zindex`, `zroll`, `zcleartomark`.
- Private operators: `zclear_stack`, `zcount`, `zmark`, `zcounttomark`.
- Registered through `zstack_op_defs`.

## Implementation Notes
- Uses `check_op`, `push`, `pop`, `ref_assign_inline`, and `ref_stack_*` helpers.
- `zindex` supports references that may live in older stack blocks via `ref_stack_index`.
- `zroll` has optimized contiguous-stack paths for `mod == 1` and `mod == -1`, plus multi-block fallback using cycle rotation.
- `clear`, `count`, `mark`, `cleartomark`, and `counttomark` delegate to ref-stack primitives.

## Dependencies
Depends on Ghostscript interpreter stack machinery in `istack.h`, refs/storage helpers in `store.h`, allocator headers, and operator registration in `oper.h`.

## Risks and Notes
- `zroll` is stack-boundary-sensitive and manually handles non-contiguous stack blocks.
- Overflow handling uses `o_stack.requested` before returning `e_stackoverflow`.
- Filesystem relevance: none directly; this is interpreter stack infrastructure.
