# File Research: sources/virtualization/spdk/lib/nvme/nvme_tcp.c

Implements SPDK's NVMe/TCP initiator transport and registers it through `SPDK_NVME_TRANSPORT_REGISTER(tcp, &tcp_ops)`. The file owns TCP socket connection setup, ICReq/ICResp negotiation, NVMe-oF Fabric CONNECT, optional authentication, PDU parsing/validation, request serialization, H2C/C2H data movement, digest handling, TLS PSK setup, poll-group socket polling, stats, and trace registration.

Key structures:
- `nvme_tcp_ctrlr`: embeds `spdk_nvme_ctrlr` and stores TLS PSK identity/key/cipher-suite state.
- `nvme_tcp_qpair`: embeds `spdk_nvme_qpair`, owns socket, request pools, send queue, receive/send PDUs, PDU receive state, negotiated digest and data limits, connection state, polling and timeout list links, stats pointer, and async completion count.
- `nvme_tcp_req`: per-command state including NVMe request pointer, CID, transfer tags, offsets, R2T tracking, ordering bits, payload iovs, response cache, and PDU pointer.

Connection flow:
- `nvme_tcp_ctrlr_construct()` allocates controller state, optionally derives TLS credentials from an NVMe TCP interchange PSK, clamps ACK timeout, initializes generic controller state, marks accel-sequence support, creates admin qpair, and registers the process.
- `nvme_tcp_qpair_connect_sock()` parses destination/source addresses, chooses SSL socket implementation when PSK is configured, sets socket options including priority, zero-copy for IO qpairs, source address/port, ACK timeout, and connect timeout, then starts async connect.
- `nvme_tcp_sock_connect_cb_fn()` moves to `INITIALIZING` and sends ICReq.
- `nvme_tcp_icresp_handle()` validates protocol format version, `maxh2cdata`, `cpda`, negotiates header/data digests, adjusts receive buffer sizing, then advances to Fabric CONNECT once ICReq send is acknowledged.
- `nvme_tcp_ctrlr_connect_qpair_poll()` drives socket connecting, ICReq timeout, Fabric CONNECT send/poll, optional authentication, and final connected state.

Request submission:
- `nvme_tcp_alloc_reqs()` creates cacheline-aligned request array and DMA PDU buffers.
- `nvme_tcp_req_init()` assigns CID, builds NVMe TCP transport SGL descriptors, and decides whether host-to-controller data can be sent as in-capsule data.
- Supports contiguous, callback SGL, and iovec payloads; controller-to-host payload iovs are built when C2H data arrives.
- Memory-domain payloads are translated to the system domain through `nvme_tcp_try_memory_translation()`.
- `nvme_tcp_qpair_capsule_cmd_send()` creates Capsule Command PDUs, handles padding and digests, attaches in-capsule data when applicable, and sends asynchronously.

PDU handling:
- Receive state machine: `AWAIT_PDU_READY`, common header, protocol-specific header, request buffer/data, quiescing, and error.
- `nvme_tcp_pdu_ch_handle()` validates PDU type, header length, payload length, and sequence legality, sending H2C TermReq on protocol errors.
- `nvme_tcp_pdu_psh_handle()` verifies header digest when present and dispatches ICResp, Capsule Response, C2H Data, C2H TermReq, or R2T.
- `nvme_tcp_c2h_data_hdr_handle()` validates CID, flags, `datao`, `datal`, range, and maps target data into request payload iovs.
- `nvme_tcp_r2t_hdr_handle()` validates R2T offset/length and max active R2T count, supports a queued subsequent R2T while waiting for H2C send acknowledgement, and sends H2C Data PDUs.
- `nvme_tcp_pdu_payload_handle()` validates data digest when enabled and completes payload processing.

Completion ordering:
- TCP requests complete only when send acknowledgement, data/response receipt, and any accel operation have all completed.
- `nvme_tcp_req_complete_safe()` centralizes this gate.
- `nvme_tcp_qpair_cmd_send_complete()` handles command send acknowledgement and may trigger deferred H2C send after R2T.
- `nvme_tcp_c2h_data_payload_handle()` and `nvme_tcp_capsule_resp_hdr_handle()` set response/data receipt and may finish/reverse accel sequences before completing.
- `nvme_tcp_req_complete()` removes the request from outstanding list, updates queue depth and tracepoints, returns it to the free list, and calls the original NVMe callback.

Digest and accel behavior:
- Header digest is computed inline when negotiated.
- Data digest may use accel `append_crc32c` when available and constraints are met, falling back to software CRC32C on resource exhaustion.
- Existing request accel sequences are finished before transmitting host-to-controller data and reversed before completing controller-to-host transfers.

Disconnect and failure:
- `nvme_tcp_ctrlr_disconnect_qpair()` removes sockets from poll groups, closes sockets, clears send queue, aborts requests, and either quiesces async qpairs or completes disconnect immediately for synchronous paths.
- `nvme_tcp_qpair_abort_reqs()` completes non-accel in-flight requests with aborted status.
- Quiescing waits for outstanding requests, especially accel-backed ones, before moving receive state to error and final disconnect.
- Transport errors set `SPDK_NVME_QPAIR_FAILURE_UNKNOWN` and disconnect the qpair.

Poll groups, stats, and trace:
- Poll groups own an SPDK socket group, `needs_poll` list for qpairs that require progress without socket events, timeout-enabled list, and aggregate TCP stats.
- `nvme_tcp_poll_group_process_completions()` polls socket events, handles disconnected qpairs, forces polling for `needs_poll`, runs timeout checks, and accumulates socket/NVMe completion stats.
- `nvme_tcp_poll_group_get_stats()` snapshots TCP stats into generic transport stats.
- `nvme_tcp_trace()` registers TCP submit/complete tracepoints and relations to socket request tracepoints.

Transport ops:
- Implements controller construct/destruct/enable, fabric register access helpers, max transfer/SGE reporting, IO qpair lifecycle, system memory-domain reporting, qpair submit/poll/reset/abort/authenticate, admin AER abort, poll-group lifecycle/stats, and trace registration.
- No interrupt fd support is implemented here; socket poll groups are the primary event path.

Filesystem/storage relevance:
- This is the TCP remote block transport for NVMe namespaces. It is critical to storage behavior because it converts NVMe requests into TCP PDUs, handles target-driven reads/writes through C2H/H2C flows, enforces protocol correctness, manages data integrity digests, and determines error/reconnect semantics exposed to upper storage users.
