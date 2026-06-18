# File Research: sources/os/bsd/netbsd-src/sys/sys/un.h

Read completely: 112 lines.

Defines UNIX-domain socket address ABI and socket options.

Key elements:
- Defines `sa_family_t` if needed.
- `SUNPATHLEN` is fixed at 104 for binary compatibility.
- `struct sockaddr_un` stores sockaddr length, address family, and path.
- NetBSD source mode defines `SOL_LOCAL` and local socket options for credentials, connect-wait, peer IDs, and credential passing.
- `struct unpcbid` stores peer pid, effective uid, and effective gid.
- Kernel declarations cover Unix-domain protocol request table, control output, initialization, locks, connect, socket-to-socket connect, mbuf disposal, and rights/credential externalization.
- Userland NetBSD mode defines `SUN_LEN()`.

Risks and notes:
- Path length remains artificially limited for compatibility.
- Credential-passing options affect security boundaries between local processes.
