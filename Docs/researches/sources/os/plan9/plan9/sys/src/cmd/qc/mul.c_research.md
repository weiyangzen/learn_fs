# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/mul.c

Constant-multiply sequence generator for replacing multiplication by constants with shifts, adds, and subtracts.

Key responsibilities:
- Caches generated multiply sequences in `multab`.
- Searches for short expression sequences using an internal two-register model.
- Uses an exception hint table for constants the bounded search does not find efficiently.
- Supports recursive handling of even constants by generating a sequence for the odd factor and appending a shift.
- Encodes sequence steps compactly as two-character operations consumed later by `mulcon()` in `swt.c`.

Dependencies:
- Uses `Multab`, `Hintab`, `Node`, diagnostics, and `gc.h` globals.
- The generated mini-language is interpreted by `qc/swt.c`.

Notable risks:
- Only searches up to short fixed lengths, with special hints for gaps.
- Negative constants are normalized for search and handled during code emission.
- Correctness relies on `docode()` validating generated and hinted sequences against the desired constant.
