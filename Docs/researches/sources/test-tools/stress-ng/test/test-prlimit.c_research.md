<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-prlimit.c -->
# sources/test-tools/stress-ng/test/test-prlimit.c

Purpose: minimal stress-ng configure probe for the resource-limit API; it compiles and often lightly invokes `prlimit`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/time.h`, `sys/resource.h`, `sys/types.h`, `unistd.h`; uses types `struct rlimit`, `pid_t`; defines `main`; calls `getpid`, `prlimit`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/time.h`, `sys/resource.h`, `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-prlimit.c -->
