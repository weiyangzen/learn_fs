# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/machcap.c

Machine-capability predicate for the PowerPC C compiler backend.

Key responsibilities:
- Reports which AST operations the target backend can lower directly.
- Accepts integer/logical arithmetic, multiply, shifts, casts between 32-bit and 64-bit families, boolean/control expression nodes, assignment operators, increments/decrements, and comparisons.
- Rejects divide/modulo operations and their assignment forms, forcing generic or runtime handling elsewhere.

Dependencies:
- Uses `Node` operation codes and type classification tables from `gc.h`, including `typev`, `typefd`, and `typechl`.

Notable risks:
- This is a policy gate for code generation. Incorrectly returning true for unsupported operations can route code into missing backend paths.
- Division/modulo are explicitly not machine-capable despite the backend containing low-level PowerPC divide opcodes in other contexts.
