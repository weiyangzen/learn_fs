<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pid_type.c -->
# sources/test-tools/stress-ng/test/test-pid_type.c

Purpose: compile-time availability probe for `enum __pid_type` associated with `pid_type`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `fcntl.h`; uses types `enum __pid_type`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pid_type.c -->
