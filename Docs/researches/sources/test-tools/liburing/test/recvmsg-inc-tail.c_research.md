# sources/test-tools/liburing/test/recvmsg-inc-tail.c

Purpose: verifies `recvmsg` multishot with incremental provided buffers retires a too-small buffer tail instead of returning spurious `-EFAULT`. It targets the case where the remaining tail is smaller than the header area needed for `struct io_uring_recvmsg_out` plus address/control metadata.

Important APIs and types: `io_uring_register_buf_ring` with `IOU_PBUF_RING_INC`, `io_uring_buf_reg.min_left`, `io_uring_prep_recvmsg_multishot`, `io_uring_recvmsg_validate`, `io_uring_recvmsg_payload`, `io_uring_recvmsg_payload_length`, `IOSQE_BUFFER_SELECT`, and stream socket pairs.

Control flow: `setup_buf_ring()` maps four 1024-byte buffers and a buffer ring, sets `min_left = 32`, registers bgid 1 as incremental, and publishes four entries. `test()` submits one recvmsg multishot on a stream socket, then writes two 480-byte payloads and seven 305-byte payloads. The payload sizes are chosen so bid 0 is consumed exactly by two large CQEs, while three small CQEs leave a 13-byte tail in bids 1 and 2, forcing retire-to-next-buffer behavior. Each CQE must succeed, include a buffer id matching the expected bid sequence `{0,0,1,1,1,2,2,2,3}`, validate as recvmsg output, have zero controllen, and match the stream payload at the expected cursor.

State and persistence: `bid_offset[]` tracks consumed bytes within each incremental buffer for validating in-buffer layout. `stream_cursor` and `sent_offset` track expected payload ordering.

Dependencies and integration: requires incremental buffer rings and recvmsg multishot; `-EINVAL` or `-ENOTSUP` skips. Uses mmap-backed buffers and helper-created stream socket pairs.

Risks and test signals: a negative CQE, wrong bid transition, invalid recvmsg layout, payload mismatch, or too few distinct bids fails. Passing proves tail retirement avoids bad-address failures and preserves payload placement.
