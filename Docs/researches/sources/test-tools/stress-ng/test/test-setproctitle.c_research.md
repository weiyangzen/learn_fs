<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setproctitle.c -->
# sources/test-tools/stress-ng/test/test-setproctitle.c

Purpose: minimal stress-ng configure probe for `setproctitle`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `bsd/unistd.h`; defines `main`; calls `setproctitle_init`, `setproctitle`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `unistd.h`, `bsd/unistd.h`; preprocessor availability gates such as `#if !(defined(__APPLE__) || \`, `#if !(defined(__APPLE__) || \`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setproctitle.c -->
