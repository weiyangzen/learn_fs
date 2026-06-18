<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rtime.c -->
# sources/user-network-fs/libtirpc/src/rtime.c

Purpose: implements the legacy `rtime()` client for the RFC 868 time service over IPv4 TCP or UDP, converting seconds since 1900 to Unix epoch seconds.

Important APIs and functions: `rtime(struct sockaddr_in *addrp, struct timeval *timep, struct timeval *timeout)` performs the query. `do_close()` closes a socket while preserving `errno`.

Control flow: a null timeout selects TCP; a non-null timeout selects UDP. The function opens an IPv4 socket, sets the target family and service port from `getservbyname("time", "tcp")`, sends a UDP probe and polls for a response or connects/reads over TCP, validates that exactly four bytes were received, converts from network byte order, subtracts the 1900-to-1970 offset, and writes `timep`.

State and persistence: no global state. It mutates `addrp->sin_family` and `addrp->sin_port` and writes `timep`.

Dependencies and integration points: uses sockets, `poll`, `/etc/services` service lookup, and IPv4 sockaddr structures. It is a standalone legacy utility rather than RPC protocol logic.

Risks: IPv4-only, depends on the deprecated time service, and calculates UDP timeout milliseconds with potential integer overflow for very large timeouts. The UDP request sends an uninitialized `thetime` buffer, which is conventional for the service but still awkward for analysis tools.

Test signals: TCP and UDP time service fixtures, timeout maps to `ETIMEDOUT`, short-read maps to `EIO`, `getservbyname` failure, EINTR during poll, and epoch conversion for known RFC 868 timestamps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rtime.c -->
