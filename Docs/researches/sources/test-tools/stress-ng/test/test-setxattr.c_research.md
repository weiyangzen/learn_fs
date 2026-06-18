<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setxattr.c -->
# sources/test-tools/stress-ng/test/test-setxattr.c

Purpose: minimal stress-ng configure probe for the extended-attribute set API; it compiles and often lightly invokes `setxattr`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`; defines `main`; calls `setxattr`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setxattr.c -->
