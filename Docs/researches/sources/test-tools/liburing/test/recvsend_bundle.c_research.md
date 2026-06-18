# sources/test-tools/liburing/test/recvsend_bundle.c

Purpose: tests send and receive bundles with normal provided buffer rings and classic provided buffers over both TCP and UDP. It validates buffer-id ordering, sequence integrity, bundle re-submission, and behavior when the socket send queue is full or almost full.

Important APIs and types: `io_uring_prep_send_bundle`, `io_uring_prep_send`, `io_uring_prep_recv_multishot`, `io_uring_setup_buf_ring`, `io_uring_prep_provide_buffers`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `IORING_FEAT_RECVSEND_BUNDLE`, TCP/UDP sockets, and pthread barriers.

Control flow: `recv_fn()` creates the receive ring, registers either a buffer ring with `RECV_BIDS` 128-byte entries or classic buffers, binds/listens or binds UDP, accepts/uses the socket, arms multishot recv, and validates completions. `do_recv()` checks selected bid equals the next expected bid, validates sequence data in message-sized chunks, advances expected bid based on bytes received, and rearms recv when `MORE` is absent before all expected bytes arrive. `do_send()` registers send buffers, optionally fills the socket send queue with nonblocking sends, populates bundle payloads with sequence numbers, then uses bundled or individual selected-buffer sends. `run_tests()` covers baseline, recv bundle, both bundles, full socket, almost-full socket, and larger-than-fast-iov segment counts. `main()` runs TCP and UDP with buffer rings, then TCP and UDP with classic provided buffers.

State and persistence: global `use_tcp`, `classic_buffers`, `nr_msgs`, and `use_port` select matrix state. `recv_data` carries synchronization, expected sequence, remaining bytes, and flags for send/recv bundle. Buffer IDs persist as ordering evidence.

Dependencies and integration: requires receive/send bundle feature for bundle cases. UDP skips backlog pressure cases because they are not reliable. Unsupported bundle marks `no_send_mshot` and produces a skip after joining the receiver.

Risks and test signals: wrong bid sequencing, oversized non-bundled receive, sequence mismatch, bad send results, or deadlock across barriers fail. Passing gives cross-protocol evidence that bundled send/recv works with both buffer ring styles and handles socket pressure.
