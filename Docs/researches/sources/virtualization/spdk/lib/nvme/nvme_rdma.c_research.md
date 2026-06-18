# File Research: sources/virtualization/spdk/lib/nvme/nvme_rdma.c

Implements SPDK's NVMe-oF RDMA initiator transport and registers it through `SPDK_NVME_TRANSPORT_REGISTER(rdma, &rdma_ops)`. The file owns RDMA-specific controller, qpair, poll-group, request, response, memory-registration, connection, completion, and teardown behavior behind the generic NVMe transport interface.

Key structures:
- `nvme_rdma_ctrlr`: embeds `spdk_nvme_ctrlr`, tracks max SGE, RDMA CM channel, and queued/free CM event wrappers.
- `nvme_rdma_qpair`: embeds `spdk_nvme_qpair`, owns RDMA CM ID, provider QP, CQ/channel, SRQ association, request/response pools, memory map, outstanding/free request lists, state, retry, and disconnect bookkeeping.
- `nvme_rdma_poller` and `nvme_rdma_poll_group`: share CQs/SRQs per RDMA device and coordinate active, connecting, and disconnected qpairs.
- `spdk_nvme_rdma_req` and `spdk_nvme_rdma_rsp`: per-command send and receive WR context, with completion flags used to wait for both SEND and RECV completion before completing an NVMe request.

Connection flow:
- `nvme_rdma_ctrlr_construct()` allocates the RDMA controller, clamps retry and ACK timeout options, discovers RDMA devices to determine `max_sge`, initializes generic controller state, creates a nonblocking RDMA CM event channel, creates admin qpair, and registers the process.
- `nvme_rdma_ctrlr_connect_qpair()` parses destination/source addresses, creates an RDMA CM ID, starts address resolution, and enqueues qpairs into a poll-group connecting list when applicable.
- `nvme_rdma_process_event_start()` and `nvme_rdma_process_event_poll()` drive async RDMA CM events through expected states. Stale connection rejection is treated specially with retry and lingering cleanup.
- `nvme_rdma_qpair_init()` creates or attaches to CQ/SRQ resources, gets a protection domain via hooks or SPDK RDMA utils, creates the provider QP, records QP number, and inserts SRQ qpairs into an RB tree for completion lookup.
- After RDMA connection establishment, `nvme_rdma_connect_established()` creates the memory map, request pool, response buffers, posts receives, then moves to Fabric CONNECT send/poll and optional authentication states.

Request construction:
- Supports null, contiguous, callback SGL, and iovec payloads.
- Uses keyed SGLs for normal RDMA data transfer, and inline in-capsule data when the operation is host-to-controller, payload fits `ioccsz_bytes`, and `icdoff == 0`.
- Enforces `NVME_RDMA_MAX_KEYED_SGL_LENGTH`, controller SGE limits, and capsule descriptor size.
- `nvme_rdma_get_memory_translation()` either translates a caller memory domain into RDMA keys or uses the qpair memory map.
- Optional accel/UMR path uses poll-group accel hooks to create per-I/O virtual contiguous memory and reverses sequences for controller-to-host data.

Completion flow:
- SEND and RECV work completions are processed either per-qpair or through shared pollers.
- `nvme_rdma_process_recv_completion()` stores the NVMe completion, reposts receives when safe, and completes only after SEND completion has also arrived.
- `nvme_rdma_process_send_completion()` marks SEND completion and similarly waits for RECV completion.
- `nvme_rdma_request_ready()` handles memory-domain transfer callbacks or completes the NVMe request.
- Completion errors map to transport failure and trigger qpair disconnect.

Disconnect and failure handling:
- Qpairs move through `EXITING`, `LINGERING`, and `EXITED`; lingering avoids freeing WR memory while shared CQ completions may still reference it.
- Stale connection retry has a separate `STALE_CONN` and `STALE_CONN_LINGERING` path to avoid use-after-free when reconnecting after rejected stale CM state.
- `nvme_rdma_qpair_abort_reqs()` completes outstanding requests with aborted status but avoids aborting in-progress accel transfers until safe.
- Destruction carefully acknowledges CM events, removes pending events, destroys QP/CQ/channel, releases poller/SRQ references, frees request/response pools, frees memory maps, releases PD, and destroys CM ID last.

Poll groups and stats:
- A poll group holds one poller per RDMA device. Pollers may own shared CQs and optional SRQs.
- Shared SRQ mode maps completions back to qpairs by QP number using an RB tree.
- `nvme_rdma_poll_group_process_completions()` handles disconnected qpairs, connecting qpairs, CM events, CQ polling, active qpair submit flushing, receive reposting, and timeout checks.
- `nvme_rdma_poll_group_get_stats()` reports per-device polls, idle polls, completions, queued requests, and RDMA send/recv WR and doorbell counters.

Transport ops:
- Implements controller construct/destruct/enable/interrupts, register access through fabrics helpers, max transfer/SGE reporting, IO qpair create/delete/connect/disconnect, memory-domain reporting, transport event processing, qpair submit/poll/reset/abort/authenticate, admin AER abort, and poll-group lifecycle/stats.
- `spdk_nvme_rdma_init_hooks()` stores external RDMA hooks globally in `g_nvme_hooks`.

Filesystem/storage relevance:
- This is a host-side remote block storage transport for NVMe namespaces over RDMA. It is not a filesystem implementation, but it is directly in the storage substrate path: request payload mapping, DMA memory registration, transport recovery, and completion behavior all affect block I/O visibility and latency to higher layers.
