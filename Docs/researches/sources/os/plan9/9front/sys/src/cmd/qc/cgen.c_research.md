# File Research: sources/os/plan9/9front/sys/src/cmd/qc/cgen.c

Core expression code generator for the Power C compiler backend. It lowers C AST nodes into target-neutral backend calls such as `gmove`, `gopcode`, `gbranch`, `patch`, and structure copy helpers.

Key responsibilities:
- `cgen` handles scalar expressions, assignments, arithmetic, calls, indirection, casts, conditionals, increments/decrements, bitfields, and 64-bit dispatch.
- `genasop` implements compound assignments while preserving left-side side effects.
- `reglcgen` and `lcgen` compute lvalues/addresses.
- `boolgen` and `bcgen` generate conditional branches and boolean materialization.
- `sugen` handles structure/union copies, structure literals, function returns by hidden pointer, and rathole temporaries.
- `layout` emits unrolled word-copy loops for larger aggregate copies.
- `cmpv`, `testv`, `cgen64`, and helpers implement `vlong`/`uvlong` comparison, constants, casts, calls, and register-pair handling.

Dependencies and coupling:
- Relies heavily on `txt.c` for actual instruction selection/emission and `swt.c` for bitfield support.
- Depends on common `cc` AST/type metadata and `gc.h` backend structures.
- Uses Power-specific 32-bit halves for 64-bit values, with endian checks via `align(..., Aarg1)`.

Notable behavior:
- Complex function-call subexpressions are spilled to stack temporaries to protect evaluation order.
- Some comments mark rough edges, such as function returns clobbering ratholes and incomplete float/vlong conversion handling.
