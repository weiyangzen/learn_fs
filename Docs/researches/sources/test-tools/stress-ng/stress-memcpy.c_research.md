# sources/test-tools/stress-ng/stress-memcpy.c

Purpose: implements `memcpy`, a memory/cache stressor and optional correctness harness for copy/move routines. It compares libc, compiler builtins, and naive implementations at several optimization levels.

Important APIs/types/functions: generated naive `memcpy` and `memmove` functions are created by `TEST_NAIVE_MEMCPY` and `TEST_NAIVE_MEMMOVE`. `memcpy_check_func()` and `memmove_check_func()` validate content and return value when verification is enabled; no-check variants remove overhead. `stress_memcpy_libc()`, `stress_memcpy_builtin()`, and macro-generated methods run fixed copy/move sequences. `stress_memcpy_all()` rotates through methods.

Control flow: the stressor maps one buffer split into three 2048-byte regions, seeds one region, chooses verification wrappers based on global flags, resolves `memcpy-method`, synchronizes, then repeatedly performs full, half, forward-overlap, and backward-overlap copies/moves for `MEMCPY_LOOPS` rounds per bogo operation.

State and persistence: static strings hold current stressor/method names for diagnostics; `memcpy_okay` stops the loop on verification failure. Mapped memory is anonymous and unmapped at exit.

Dependencies/integration: uses core mmap and target-clone support, compiler builtin detection, stress-ng method option lookup, verification flags, proc-state sync, and bogo counters.

Risks/test signals: only `memmove` is used for overlapping ranges; changing those to `memcpy` would be undefined. Useful signals are optional verification failures with method names, method enumeration for all variants, mmap resource behavior, and continued bogo operations while `memcpy_okay` is true.
