# File Research: sources/os/linux/linux/io_uring/net.c

Networking opcode implementation for io_uring: shutdown, send/sendmsg, recv/recvmsg, accept, socket, connect, zerocopy send, zerocopy receive, bind, and listen.

Key flows:
- Send prep imports address/iovecs or fixed buffers, supports buffer selection for `SEND`, bundle sends, vectorized sends, compat control handling, and `MSG_NOSIGNAL`.
- Send issue handles poll-first, nonblocking `MSG_DONTWAIT`, `MSG_WAITALL` retry semantics, partial accounting, bundle CQEs, buffer commit/recycle, and async iovec cache recycling.
- Recv prep validates multishot requirements, buffer selection, bundle restrictions, optional byte limits, compat msghdr handling, and allocates `io_async_msghdr`.
- Recv issue supports single and multishot recv/recvmsg, selected buffers, recvmsg multishot headers, bundle receive retries, socket nonempty CQE flags, fairness cap via `MULTISHOT_MAX_RETRY`, and `IOU_REQUEUE`.
- Zerocopy receive requires multishot and delegates to `io_zcrx_recv()`.
- Zerocopy send allocates a notification request, configures `ubuf_info`, supports report-usage flags, registered/fixed buffers, custom skb scatterlist filling, and posts primary CQE with `IORING_CQE_F_MORE`.
- Accept supports normal fd install or fixed-file install, multishot accept, poll-first, dontwait, and socket-nonempty CQE flags.
- Socket supports normal or fixed-file creation and BPF filter population.
- Connect stores sockaddr in async data, retries in-progress nonblocking connects, handles `-ECONNABORTED` once, and resolves final socket error for in-progress cases.
- Bind forces async for pathname AF_UNIX binds to avoid lockdep write-lock issues.
- Listen wraps socket listen and reports direct result.

Important details:
- `io_async_msghdr` objects are recycled through `ctx->netmsg_cache`.
- `io_sendrecv_fail()` preserves partial progress and zerocopy notification semantics on failure.
- Many op-specific flags are stored in SQE `ioprio`, so validation masks lower UAPI bits and internal retry bits separately.
- `io_net_retry()` limits WAITALL retry behavior to stream and seqpacket sockets.
