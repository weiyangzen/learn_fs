<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_minflt.c -->
# sources/test-tools/stress-ng/test/test-rusage_ru_minflt.c

Purpose: compile-time availability probe for `struct rusage` associated with `rusage_ru_minflt`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/time.h`, `sys/resource.h`, `string.h`; uses types `struct rusage`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/time.h`, `sys/resource.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_minflt.c -->
