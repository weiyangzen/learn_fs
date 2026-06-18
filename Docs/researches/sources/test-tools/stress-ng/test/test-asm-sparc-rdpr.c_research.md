# sources/test-tools/stress-ng/test/test-asm-sparc-rdpr.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-sparc-rdpr`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rdpr %%ver, %0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `sparc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
