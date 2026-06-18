<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syscall.c -->
# sources/test-tools/stress-ng/test/test-syscall.c

Purpose: minimal stress-ng configure probe for `syscall`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/syscall.h`, `unistd.h`; defines `main`; calls `syscall`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_getpid` through `syscall()`.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/syscall.h`, `unistd.h`; architecture syscall numbers `__NR_getpid`; preprocessor availability gates such as `#if defined(__NR_getpid)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. Test signals are successful compilation; successful linking; the expected syscall symbol being present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syscall.c -->
