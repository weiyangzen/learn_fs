# File Research: sources/virtualization/spdk/lib/nvme/nvme_transport.c

Implements the generic NVMe transport registry and dispatch layer used by PCIe, RDMA, TCP, and other transports. It stores registered transport ops, exposes availability queries, wraps controller/qpair operations, handles poll-group membership state, and stores process-wide transport options.

Registry:
- `g_spdk_nvme_transports` is a global TAILQ of registered transports.
- `g_transports` is a fixed array of 16 transport slots.
- `spdk_nvme_transport_register()` rejects duplicate transport names and over-capacity registration, then copies the ops table and appends it to the registry.
- `nvme_get_transport()` performs case-insensitive lookup by transport name; helpers expose first/next iteration and availability by type or name.

Controller dispatch:
- Construction, scan, attached scan, destruct, enable, readiness, register access, CMB/PMR operations, max transfer size, max SGEs, memory-domain reporting, and transport-event processing are all routed to transport ops.
- Optional ops return explicit unsupported defaults such as `-ENOTSUP`, `-ENOSYS`, `NULL`, or `0` depending on semantics.
- Async register operations fall back to synchronous op execution followed by a queued synthetic completion via `nvme_queue_register_operation_completion()`.

Qpair lifecycle:
- `nvme_transport_ctrlr_create_io_qpair()` delegates qpair creation and stores the transport pointer on non-admin qpairs for fast IO-path dispatch.
- Delete deliberately looks up the transport by controller TRID instead of trusting `qpair->transport`, because multiprocess PCIe cases can invalidate function-pointer objects across processes.
- Connect sets qpair state to connecting, clears current transport failure reason while saving the previous one, invokes transport connect, attaches poll-group state, and busy-polls synchronous connects until the qpair leaves connecting state.
- Connect failure restores the saved failure reason and disconnects.
- Disconnect moves the qpair to disconnecting, updates poll-group membership when owned by the active process, and delegates transport-specific disconnect.
- `nvme_transport_ctrlr_disconnect_qpair_done()` aborts queued requests for the active process/admin queue, marks disconnected, wakes poll-group disconnect handling, and cleans up outstanding fabric/auth polling state.

Qpair operation dispatch:
- Abort, reset, submit, process completions, and iterate requests use `qpair->transport` for non-admin qpairs and lookup-by-controller for admin qpairs.
- Authentication and admin AER abort are dispatched through transport ops.
- Qpair fd retrieval is optional and returns `-ENOTSUP` when absent.

Poll groups:
- `nvme_transport_poll_group_create()` delegates creation, records the transport, initializes connected/disconnected qpair lists, and starts connected count at zero.
- Add/remove operate only on disconnected qpairs.
- Connect/disconnect transitions move qpairs between connected and disconnected STAILQs and maintain `num_connected_qpairs`.
- Completion processing, disconnected qpair checks, destroy, stats get/free are delegated to transport ops.

Transport options:
- Global defaults: RDMA SRQ size `0`, RDMA max CQ size `0`, RDMA CM event timeout `1000 ms`, RDMA UMR-per-I/O disabled, TCP connect timeout `0`.
- `spdk_nvme_transport_get_opts()` and `spdk_nvme_transport_set_opts()` copy fields based on struct size/offset for ABI compatibility.
- Setter validates `tcp_connect_timeout_ms <= INT_MAX`.
- Static assert requires `spdk_nvme_transport_opts` size to remain 32 bytes unless copy logic is updated.

Filesystem/storage relevance:
- This file is the common transport abstraction for all SPDK NVMe block-device access. It does not move data itself, but it defines how higher-level NVMe controller and qpair code interacts with local and fabric transports, including connection state, polling, failure, options, and stats routing.
