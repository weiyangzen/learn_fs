<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-random.c -->
# sources/test-tools/stress-ng/test/test-random.c

Purpose: minimal stress-ng configure probe for the libc PRNG API; it compiles and often lightly invokes `random`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `random`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-random.c -->
