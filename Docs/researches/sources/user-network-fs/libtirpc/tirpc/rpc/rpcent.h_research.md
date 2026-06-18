# sources/user-network-fs/libtirpc/tirpc/rpc/rpcent.h

Purpose: `rpcent.h` exposes RPC program-name database lookup compatibility APIs when the system C library does not provide them.

Important APIs, types, and functions: When enabled by platform macros, it defines `struct rpcent` and declares `getrpcbyname`, `getrpcbynumber`, `getrpcent`, `setrpcent`, and `endrpcent`.

Control flow: Callers iterate or look up `/etc/rpc`-style entries by name or number using static-storage legacy APIs.

State and persistence behavior: The declared lookup functions return pointers to static areas and are documented as MT-unsafe. Iteration state is implementation-owned.

Dependencies and integration points: It is included by `rpc.h` and provides fallback compatibility for libc configurations without RPC netdb support.

Risks: Conditional declarations vary by libc and feature macros, which can create portability surprises. Static returned storage is not thread-safe and is overwritten by subsequent calls.

Test signals: Build tests should cover glibc, uClibc-without-RPC, and non-glibc configurations. Runtime tests should verify lookup by name/number, iteration reset, and documented static-storage behavior.
