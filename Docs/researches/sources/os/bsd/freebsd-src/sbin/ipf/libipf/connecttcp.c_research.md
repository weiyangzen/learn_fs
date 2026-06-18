# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/connecttcp.c

This helper opens a TCP connection to an IPv4 server and port.

`connecttcp()` accepts either numeric dotted IPv4 or hostname, resolves it into `sockaddr_in`, creates an AF_INET stream socket, connects, and returns the descriptor or `-1`.

It masks the supplied port to 16 bits before `htons()`.
