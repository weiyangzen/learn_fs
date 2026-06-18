# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/remotehost.c

- Role: Discovers the peer hostname for an accepted network connection on fd 0.
- Key function: `getremotehostname(name, nname)` defaults to `unknown`, calls `getpeername` and `gethostbyaddr`, then enables `SO_KEEPALIVE` and optionally `TCP_NODELAY`.
- Integration: `u9fs.c` calls it when network mode is enabled; authentication modules can use `remotehostname`.
- Risks/notes: Reverse DNS failure leaves `unknown`; socket option errors are ignored.
