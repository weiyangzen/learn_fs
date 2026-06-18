<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mquery.c -->
# sources/test-tools/stress-ng/test/test-mquery.c

Purpose: minimal stress-ng configure probe for `mquery`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `stdlib.h`, `sys/mman.h`; defines `main`; calls `mquery`; references constants/macros `PROT_READ`, `MAP_FIXED`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mquery.c -->
