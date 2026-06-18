<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-off64_t.c -->
# sources/test-tools/stress-ng/test/test-off64_t.c

Purpose: compile-time availability probe for `off64_t` associated with `off64_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/types.h`; uses types `off64_t`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`; preprocessor availability gates such as `#ifndef _LARGEFILE_SOURCE`, `#ifndef _LARGEFILE64_SOURCE`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-off64_t.c -->
