# sources/test-tools/strace/tests/net-yy-unix.c

Purpose: tests rich `strace -yy` UNIX socket endpoint annotations, including socket protocol names, inode pairs, pathname endpoints, and auto-bound abstract names.

Important APIs, types, and helpers: `socket(AF_UNIX)`, optional `getxattr("system.sockprotoname")`, `bind`, `listen`, `getsockopt`, `getsockname`, `connect`, `accept4`, `getpeername`, `setsockopt(SO_PASSCRED)`, `sendto`, `recvfrom`, `close`, `unlink`, `inode_of_sockfd`, `xasprintf`, and tail allocation helpers.

Control flow: creates a pathname listener, discovers a socket protocol label, accepts and transfers through a first client, then creates a second client with `SO_PASSCRED` to exercise abstract peer names. Every lifecycle call is mirrored by a precise expected-output `printf`.

State and persistence: creates `net-yy-unix.socket` and removes it at the end. Descriptor state and inode relationships are runtime-only. Optional xattr lookup allocates and frees a proc fd path.

Dependencies and integration points: requires `/proc/self/fd/`, UNIX stream sockets, optional extended attributes, and the strace `-yy` fd path machinery. It is a higher-detail counterpart to `net-y-unix.c`.

Risks and edge cases: output depends on kernel support for `system.sockprotoname`, abstract auto-bind names, and stable inode relationship rendering. Cleanup is important to avoid stale socket files between runs.

Test signals: expected traces include `<UNIX:[inode,"path"]>`, connected inode arrows, optional abstract `@"..."` annotations, successful data transfers, cleanup, and `+++ exited with 0 +++`.
