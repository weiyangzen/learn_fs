<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sysinfo.c -->
# sources/test-tools/stress-ng/test/test-sysinfo.c

Purpose: minimal stress-ng configure probe for `sysinfo`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/sysinfo.h`; uses types `struct sysinfo`; defines `main`; calls `sysinfo`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/sysinfo.h`; preprocessor availability gates such as `#if defined(__sun__)`, `#error this is not the sysinfo you are looking for`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sysinfo.c -->
