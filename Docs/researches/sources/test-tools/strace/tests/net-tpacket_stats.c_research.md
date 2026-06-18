# sources/test-tools/strace/tests/net-tpacket_stats.c

Purpose: validates `getsockopt(SOL_PACKET, PACKET_STATISTICS)` decoding for packet socket statistics, including partial optlen reads and complete `tp_packets`, `tp_drops`, and `tp_freeze_q_cnt` fields.

Important APIs, types, and helpers: `getsockopt`, `struct tp_stats`, `socklen_t`, `offsetof`, `offsetofend`, `PRINT_FIELD_U`, `print_quoted_hex`, `TAIL_ALLOC_OBJECT_CONST_PTR`, and optional `INJECT_RETVAL` behavior.

Control flow: `main` allocates a stats buffer and repeatedly sets `optlen` to full, zero, truncated-at-field, exact-field, and oversized lengths. `get_tpacket_stats` performs the syscall, records/validates the return, then prints either the raw pointer, a partially quoted field, or an incrementally decoded struct based on the original optlen.

State and persistence: `errstr` is the only global state. The kernel call uses fd `-1`, so no persistent socket state is created. The function mutates local optlen variables to simulate the decoder’s view of returned lengths.

Dependencies and integration points: depends on packet socket UAPI definitions and the strace test formatting helpers. The file is also included by `net-tpacket_stats-success.c` to exercise injected success.

Risks and edge cases: most risk sits in off-by-one optlen handling around field boundaries and in differentiating failed calls from injected success. A decoder change that prints partial integers incorrectly will be caught here.

Test signals: expected output enumerates every optlen boundary and ends with `+++ exited with 0 +++`; in injected builds each syscall result must match `INJECT_RETVAL`.
