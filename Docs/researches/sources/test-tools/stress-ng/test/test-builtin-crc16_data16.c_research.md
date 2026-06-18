# sources/test-tools/stress-ng/test/test-builtin-crc16_data16.c

Purpose: compile probe for compiler builtin `crc16_data16` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_crc16_data8`; includes: `<stdint.h>`; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
