# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath1.c

## Purpose
Implements additional PostScript Level 1 path operators: arcs, arcto, path transformations, path bounding boxes, and `pathforall`.

## Key Functions
- `zarc()`, `zarcn()`, `zarct()`, and `zarcto()` implement circular/tangent path operations.
- `zdashpath()`, `zflattenpath()`, `zreversepath()`, `zstrokepath()`, and `zclippath()` transform or replace paths.
- `zpathbbox()` computes path bounding boxes.
- `zpathforall()` enumerates path elements through four user procedures.
- `path_continue()` drives path enumeration on the execution stack.
- `path_cleanup()` releases the path enumerator.

## Important Behavior
- `arcto` returns tangent points while `arct` consumes operands and returns no points.
- `pathforall` pushes a mark, four procedures, and an enumerator, then schedules continuations.
- Path enumeration checks operand-stack capacity before fetching the next path element.
- Curve elements push three points before invoking the curve procedure.

## Research Notes
Continuation-driven path iteration mirrors other interpreter `forall`-style operators.
