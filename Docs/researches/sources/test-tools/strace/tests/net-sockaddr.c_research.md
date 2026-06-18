# sources/test-tools/strace/tests/net-sockaddr.c

Purpose: exercises strace decoding of many `struct sockaddr` variants by issuing `connect(-1, sockaddr, len)` calls that reliably fail with `EBADF` while still forcing strace to inspect the user-supplied address bytes. It covers normal, truncated, oversized, abstract, and unknown address forms.

Important APIs, types, and helpers: `connect`, `sockaddr_un`, `sockaddr_in`, `sockaddr_in6`, optional `sockaddr_ipx`, AX.25 `full_sockaddr_ax25`, `sockaddr_x25`, `sockaddr_nl`, `sockaddr_ll`, optional Bluetooth HCI/SCO/RFCOMM/L2CAP structures, `TAIL_ALLOC_OBJECT_*`, `tail_memdup`, `midtail_alloc`, `fill_memory`, `pidns_print_leader`, `pidns_pid2str`, `ifindex_lo`, and endian/network helpers such as `htons`, `htonl`, `inet_addr`, and `inet_pton`.

Control flow: `main` initializes pid namespace testing, then calls per-family check functions. Each check prepares one or more address objects, varies length or field values, performs a failing `connect`, and prints the expected decoded trace line. UNIX tests cover pathname, abstract namespace, shifted pointers, and excessive/short lengths; IPv4/IPv6 tests cover full decoding and `sa_data` fallbacks; AX.25/X.25/PACKET/NETLINK/Bluetooth tests verify family-specific symbolic decoding and raw fallback behavior.

State and persistence: the test has no persistent state. It mutates stack/tail-allocated address buffers in place and prints expectations. It depends on the current pid and loopback ifindex for pid namespace and interface-name rendering, and optional compile-time feature macros gate IPX and Bluetooth cases.

Dependencies and integration points: integrates with the strace test harness through `tests.h`, `pidns.h`, `netlink.h`, allocation helpers, `RVAL_EBADF`, and generated xlat tables in strace itself. It depends on Linux UAPI headers for network families and on `/proc`/namespace support indirectly for pid and interface annotations.

Risks and edge cases: this file intentionally probes decoder boundaries: short reads, user pointers shifted near allocation tails, non-NUL UNIX names, abstract UNIX names, invalid family numbers, optional kernel header differences, and symbolic loopback rendering. Regressions are likely if sockaddr length validation, family dispatch, pid namespace translation, or optional field guards change.

Test signals: success is the exact stdout stream ending in `+++ exited with 0 +++`; the syscalls should fail consistently with `EBADF`, so the signal is decoder output rather than kernel networking success.
