# sources/test-tools/strace/tests/net-y-unix.c

Purpose: tests `strace -y` style file descriptor annotation for live UNIX stream sockets. It verifies socket inode rendering while performing a real bind/listen/connect/accept/send/receive sequence.

Important APIs, types, and helpers: `socket(AF_UNIX, SOCK_STREAM)`, `bind`, `listen`, `getsockopt(SO_PASSCRED)`, `getsockname`, `connect`, `accept4`, `getpeername`, `setsockopt`, `sendto`, `recvfrom`, `close`, `unlink`, `inode_of_sockfd`, `tail_memdup`, and `TAIL_ALLOC_OBJECT_CONST_PTR`.

Control flow: the test creates a pathname UNIX listener, prints socket fd inode annotations, accepts one normal connection, sends data, closes both ends, then repeats with `SO_PASSCRED` enabled to trigger abstract-peer behavior in accepted address reporting. It cleans up the socket pathname and prints every syscall expectation.

State and persistence: creates a temporary `net-y-unix.socket` filesystem socket and removes it at the end. Runtime state includes three socket descriptors and their inode values; no state should remain after `unlink` and `close`.

Dependencies and integration points: requires `/proc/self/fd/` for descriptor-to-inode annotation, UNIX domain sockets, and strace fd path decoding. It integrates with the broader `-y` tests by expecting `<socket:[inode]>` annotations rather than full endpoint details.

Risks and edge cases: stale socket path cleanup, accepted socket address lengths, abstract auto-bound client names, and platform differences in UNIX credential behavior can affect output. The test skips only if required proc/socket operations are unavailable.

Test signals: expected output includes fd annotations as `socket:[inode]`, successful UNIX socket lifecycle calls, a data transfer, cleanup, and `+++ exited with 0 +++`.
