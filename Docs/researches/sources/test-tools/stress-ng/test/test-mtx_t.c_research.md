<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx_t.c -->
# sources/test-tools/stress-ng/test/test-mtx_t.c

Purpose: compile-time availability probe for `mtx_t` associated with `mtx_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `threads.h`, `string.h`; uses types `mtx_t`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: uses stack-allocated C11 mutex state only.

Dependencies and integration points: depends on headers `threads.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx_t.c -->
