# sources/test-tools/liburing/examples/zcrx.c

## sources/test-tools/liburing/examples/zcrx.c

Purpose: Experimental zero-copy receive server for io_uring interface queues. It accepts TCP IPv6 connections and receives into registered zero-copy areas backed by normal memory, huge pages, or dmabuf.

Important APIs/types/functions: `struct zc_conn`; globals for queue/area config; `setup_zcrx`, `zcrx_populate_area`, `zcrx_populate_area_udmabuf`, `add_accept`, `add_recvzc`, `process_accept`, `process_recvzc`, `return_buffer`, `server_loop`; APIs `io_uring_register_ifq`, `IORING_OP_RECV_ZC`, `IORING_SETUP_CQE32`, `io_uring_zcrx_*` structures.

Control flow: parse interface, RX queue, sizes, area allocation mode, and affinity. Server creates IPv6 listener, initializes ring with CQE32 and enlarged CQ, registers zero-copy interface queue and refill ring/area, arms accept, and loops. Accepted connections allocate `zc_conn`, optionally set CPU affinity based on incoming CPU, arm multishot recvzc. Receive CQEs verify data if requested, update byte count, and return buffers through refill ring; final CQE handles completion or ENOSPC requeue.

State and persistence: listening and accepted sockets, registered interface queue, refill ring mapping, registered receive area, optional dmabuf/memfd fds, per-connection counters. No file output.

Dependencies/integration: very recent liburing/kernel zcrx APIs, network interface queue id, `/dev/udmabuf` for dmabuf mode, memfd, huge pages optionally, IPv6 TCP.

Risks: experimental kernel interface and direct CQE32 layout assumptions. `process_accept` sets `stop = false` on accept failure, likely preventing termination rather than stopping. Refill queue full drops buffers. Requires careful privileges and NIC queue setup. Cleanup is incomplete for mappings/fds on exit.

Test signals: accepted socket logs, connection termination byte/CQE/requeue stats, optional payload verification, fatal errors on setup mismatch.
