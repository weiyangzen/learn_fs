# sources/test-tools/liburing/examples/send-zerocopy.c

## sources/test-tools/liburing/examples/send-zerocopy.c

Purpose: Zerocopy send benchmark/test derived from Linux selftests. It can act as sender or receiver for TCP/UDP over IPv4/IPv6, supports fixed files, registered buffers, ring fd registration, huge pages, CPU affinity, multithreading, data verification, and defer-taskrun.

Important APIs/types/functions: `struct thread_data`; config globals; `setup_sockaddr`, `do_setup_rx`, `do_rx`, `do_tx`, `wait_cqe_fast`, `init_buffers`, `parse_opts`; `io_uring_prep_send_zc`, `IORING_RECVSEND_FIXED_BUF`, `IORING_CQE_F_NOTIF`, buffer/file/ring registration APIs.

Control flow: parse protocol/options and allocate patterned payload. Receiver mode binds/listens or binds UDP and flushes incoming data until timeout. Sender mode creates threads, connects sockets, initializes rings, registers files/ring/buffer, synchronizes via barrier, submits batches of send or send_zc SQEs until runtime/interrupt, consumes normal completions and zerocopy notification CQEs, then shuts down and prints aggregate throughput.

State and persistence: memory-mapped payload, socket connections, registered buffers/files, pthreads and barrier, counters. No file persistence.

Dependencies/integration: Linux networking, liburing zerocopy send support, optional huge pages, optional device binding, pthreads.

Risks: high-performance test with many privileged/environment-sensitive options. TCP batching can reorder data and disables verification. Signal handler uses `_exit` on second interrupt. Some error paths call fatal exit from worker threads. Receiver uses blocking `poll` and timeout assumptions.

Test signals: throughput line `packets=... rps=...`; verification failures detect payload mismatch; CQE notification accounting catches zerocopy completion semantics.
