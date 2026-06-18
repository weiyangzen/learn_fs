# sources/test-tools/stress-ng/test/test-atomic_nand_fetch.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `nand_fetch` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_nand_fetch`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
