<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mremap.c -->
# sources/test-tools/stress-ng/test/test-mremap.c

Purpose: minimal stress-ng configure probe for the Linux mapping resize API; it compiles and often lightly invokes `mremap`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `stddef.h`; defines `main`; calls `mremap`; references constants/macros `MREMAP_FIXED`, `MREMAP_MAYMOVE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`, `stddef.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mremap.c -->
