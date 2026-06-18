# sources/test-tools/strace/tests/net-tpacket_req.c

Purpose: verifies `setsockopt` decoding for `SOL_PACKET` ring setup options that carry `struct tpacket_req`, especially `PACKET_RX_RING` and, when available, `PACKET_TX_RING`.

Important APIs, types, and helpers: `setsockopt`, `SOL_PACKET`, `PACKET_RX_RING`, optional `PACKET_TX_RING`, `struct tpacket_req`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `sprintrc`, and `ARG_STR`.

Control flow: `main` calls `test_tpacket_req` for each supported option. The helper first sends an unknown option with `NULL`, then a normal `struct tpacket_req`, then an oversized optlen that should make strace print the raw pointer rather than a structured object.

State and persistence: only the global `errstr` stores the formatted syscall result between the syscall wrapper and the expected-output print. No filesystem or socket state is persisted because fd `-1` guarantees failure after argument decoding.

Dependencies and integration points: relies on Linux `if_packet.h` option definitions and the strace decoder for packet socket options. The test harness provides tail allocation and symbolic return formatting.

Risks and edge cases: the key boundary is optlen equality versus optlen larger than `sizeof(struct tpacket_req)`. Kernel/header availability of `PACKET_TX_RING` changes coverage at compile time.

Test signals: expected output should show unknown option as `PACKET_???`, normal ring fields by name, and oversized optval as `%p`, ending with `+++ exited with 0 +++`.
