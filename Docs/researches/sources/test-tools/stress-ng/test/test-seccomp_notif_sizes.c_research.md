<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-seccomp_notif_sizes.c -->
# sources/test-tools/stress-ng/test/test-seccomp_notif_sizes.c

Purpose: compile-time availability probe for `struct seccomp_notif_sizes` associated with `seccomp_notif_sizes`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `stdlib.h`, `linux/seccomp.h`; uses types `struct seccomp_notif_sizes`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `linux/seccomp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-seccomp_notif_sizes.c -->
