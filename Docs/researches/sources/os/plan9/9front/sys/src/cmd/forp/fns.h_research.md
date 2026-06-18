# File Research: sources/os/plan9/9front/sys/src/cmd/forp/fns.h

## Purpose
Declares cross-module functions for `forp`.

## Key Elements
Exposes allocation helpers, parsing, error reporting, AST construction, symbol lookup, expression conversion, assertion handling, solver driver, SAT assumptions, and Boolean/SAT logic constructors.

## Dependencies
Forward-declares `SATSolve` and depends on `dat.h` types being visible to users.

## Behavior/Risks
Varargs SAT helper prototypes rely on zero-terminated literal lists and the Plan 9 varargs conventions used in `logic.c`.
