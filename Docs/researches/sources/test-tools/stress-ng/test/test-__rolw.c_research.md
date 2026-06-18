# sources/test-tools/stress-ng/test/test-__rolw.c

Purpose: compile probe for compiler rotate intrinsic `__rolw`, checking availability of a left rotate on word-sized operands.

Important APIs/types/functions: intrinsic call `__rolw`; observed symbols: `__rolw`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
