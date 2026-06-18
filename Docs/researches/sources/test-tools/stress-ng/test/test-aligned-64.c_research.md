# sources/test-tools/stress-ng/test/test-aligned-64.c

Purpose: compile probe for alignment support `64`, covering either compiler alignment attributes or aligned allocation APIs required by stress-ng data buffers and vector-friendly structures.

Important APIs/types/functions: alignment declarations or allocation calls; observed symbols: `__attribute__`, `aligned`, `test_align64`; includes: `<stdint.h>`; macros: none.

Control flow: `main` declares or allocates an object with the requested alignment and returns after the compiler has type-checked the construct. Any free call is only cleanup for allocation probes.

State and persistence behavior: state is local stack or heap memory for the duration of the probe. No persistent resources are retained.

Dependencies and integration points: informs stress-ng whether it can request cacheline/page/large alignment in hot buffers, shared structures, or SIMD-oriented test data. Failed probes force less-specific allocation or declaration paths.

Risks and test signals: alignment syntax and maximum supported alignment vary by compiler, standard library, and target ABI. Compile/link success is the key signal; it does not guarantee every runtime allocation request will succeed under memory pressure.
