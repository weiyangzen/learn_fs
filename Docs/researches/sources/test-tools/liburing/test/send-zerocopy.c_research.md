# sources/test-tools/liburing/test/send-zerocopy.c

Purpose: comprehensive coverage of zero-copy send operations, including `SEND_ZC`, `SENDMSG_ZC`, fixed buffers, IPv4/IPv6, TCP/UDP, cork/link sequences, async mode, address passing, large/unaligned/hugetlb buffers, notification CQEs, and invalid cases.

Important APIs/types/functions: `io_uring_prep_send_zc`, `io_uring_prep_sendmsg_zc`, `io_uring_prep_send_set_addr`, `IORING_CQE_F_MORE`, `IORING_CQE_F_NOTIF`, `IORING_RECVSEND_FIXED_BUF`, `IORING_RECVSEND_POLL_FIRST`, `IORING_SEND_ZC_REPORT_USAGE`, `io_uring_register_probe`, `t_register_buffers`, and helper `t_create_socketpair_ip`.

Control flow: `probe_zc_support()` gates opcode availability. `run_basic_tests()` covers simple sends, vector sends, bad buffers/addresses/flags, async address lifetime, report-usage notification, and malformed `SENDMSG_ZC`. The main matrix then registers buffers and `test_inet_send()` iterates many combinations of socket family, connection mode, TCP/UDP, `SO_ZEROCOPY`, send/sendmsg, fixed or mixed registered buffers, corked linked requests, async, poll-first, normal/large/unaligned/huge buffers, and iovec shape.

State/persistence behavior: state is socket buffers, registered memory, CQ notification chains, and global feature flags (`has_sendzc`, `has_sendmsg`, `has_regvec`, `hit_enomem`, `no_send_vec`). No files persist.

Dependencies/integration: uses loopback sockets, memory mapping/hugetlb where available, registered buffers, and kernel zero-copy notification semantics. Some paths skip on unsupported opcodes, `-EINVAL`, unavailable memory, or memlock limits.

Risks/test signals: detects wrong send lengths, missing or extra notification CQEs, bad `F_MORE`/`F_NOTIF` sequencing, payload mismatch, stale address use, incorrect fixed-buffer handling, and kernel `-ENOMEM` resource pressure.
