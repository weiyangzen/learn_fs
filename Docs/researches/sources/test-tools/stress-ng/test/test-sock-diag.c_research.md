<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sock-diag.c -->
# sources/test-tools/stress-ng/test/test-sock-diag.c

Purpose: minimal stress-ng configure probe for `sock-diag`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`, `linux/netlink.h`, `linux/rtnetlink.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `errno.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`, `linux/netlink.h`, `linux/rtnetlink.h`, `linux/sock_diag.h`, `linux/unix_diag.h`; preprocessor availability gates such as `#if defined(__linux__)`, `#if defined(AF_NETLINK) &&		\`, `#error sock_diag not supported`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sock-diag.c -->
