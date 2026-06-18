# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/machcap.c

## Purpose
Reports whether the 386 backend has machine-specific support for selected IR operations, especially 64-bit and compound operations.

## Key Function
- `machcap(Node *n)`

## Important Behavior
- `machcap(Z)` returns true as a feature-test path.
- Returns true for:
  - integer and vlong multiplication forms,
  - 64-bit arithmetic/bitwise/shift operations on supported types,
  - casts to/from vlong/non-floating types,
  - conditionals, comma/list/logical/not/dot forms,
  - compound assignments,
  - pre/post increment/decrement,
  - relational operations.
- Returns false for unsupported node/type combinations.

## Research Notes
This is a small capability switch used by common compiler code and the 64-bit lowering path to decide when 386-specific codegen can handle an operation.
