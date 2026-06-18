<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-send-signal.c -->
# sources/test-tools/stress-ng/test/test-pidfd-send-signal.c

Purpose: minimal stress-ng configure probe for `pidfd-send-signal`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/syscall.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_pidfd_send_signal` through `syscall()`.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/syscall.h`; architecture syscall numbers `__NR_pidfd_send_signal`; preprocessor availability gates such as `#if !defined(__NR_pidfd_send_signal)`, `#error __NR_pidfd_send_signal not defined`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking; the expected syscall symbol being present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-send-signal.c -->
