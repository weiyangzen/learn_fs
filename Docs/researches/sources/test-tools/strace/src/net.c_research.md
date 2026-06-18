<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/net.c -->
# sources/test-tools/strace/src/net.c

Purpose: decodes core socket/network syscalls and many socket option payloads.
Important APIs/types/functions: `socket`, `accept/accept4`, `send/sendto`, `recv/recvfrom`, `socketpair`, `pipe/pipe2`, `getsockopt`, `setsockopt`, `decode_sockbuf`, `decode_sockname`, `print_sockopt_fd_level_name`, and numerous protocol/socket-option xlat tables.
Control flow: socket creation prints protocol names by address family; accept/getname paths save entry-side length and print changed exit lengths; send paths decode buffers immediately, receive paths decode buffers on exit; sockopt decoding switches by level/name to print typed structures, integers, fd values, filters, packet stats, TCP AO keys, TIPC groups, and defaults.
State and persistence behavior: stores entry-side socklen/optlen in `tcb` private ulong for exit-side comparison; otherwise stateless. Dependencies and integration points: sockaddr decoders, netlink decoder, BPF filter decoder, fd protocol cache, xlat tables, and iovec/string printers.
Risks: socket APIs have many level/name-specific payload sizes; malformed lengths and changed optlen values must be rendered without over-reading. Test signals: domain/protocol matrix, accept/getpeername length changes, send/recv success/error, getsockopt/setsockopt for special options, netlink sockets, and unknown option fallbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/net.c -->
