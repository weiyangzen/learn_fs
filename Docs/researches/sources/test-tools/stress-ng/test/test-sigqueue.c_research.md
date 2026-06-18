<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigqueue.c -->
# sources/test-tools/stress-ng/test/test-sigqueue.c

Purpose: minimal stress-ng configure probe for `sigqueue`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`, `signal.h`; uses types `union sigval`, `pid_t`; defines `main`; calls `getpid`, `sigqueue`; references constants/macros `SIGALRM`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`, `signal.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error sigqueue is defined but not implemented and will always fail`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigqueue.c -->
