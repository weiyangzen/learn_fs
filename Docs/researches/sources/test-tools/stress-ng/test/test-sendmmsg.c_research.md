<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendmmsg.c -->
# sources/test-tools/stress-ng/test/test-sendmmsg.c

Purpose: minimal stress-ng configure probe for the batched socket send API; it compiles and often lightly invokes `sendmmsg`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`; uses types `struct sockaddr_in`, `struct mmsghdr`, `struct iovec`, `struct sockaddr`; defines `main`; calls `memset`, `socket`, `htonl`, `htons`, `connect`, `close`, `sendmmsg`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendmmsg.c -->
