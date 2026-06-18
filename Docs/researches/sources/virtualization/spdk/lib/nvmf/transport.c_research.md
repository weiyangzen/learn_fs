# File Research: sources/virtualization/spdk/lib/nvmf/transport.c

Generic SPDK NVMe-oF transport framework implementation. This file owns transport registration, common option handling, listener lifecycle, poll-group dispatch, qpair/request forwarding, and shared iobuf buffer management used by concrete transports such as TCP.

Key responsibilities:
- Maintains the global registered transport-ops list and rejects duplicate transport names.
- Provides transport option initialization/copying with ABI-size compatibility checks.
- Creates transports synchronously or asynchronously, validates common options, initializes listener lists/mutexes, and registers iobuf modules when configured.
- Destroys transports by stopping all listeners, unregistering iobuf modules, destroying the mutex, and delegating to transport-specific `destroy`.
- Dumps common transport options to JSON and lets concrete transports append transport-specific fields.
- Manages listener refcounts, listen/stop-listen calls, and listener discovery delegation.
- Implements async stop-listen fanout that disconnects matching qpairs across poll groups before removing the listener.
- Creates/destroys generic transport poll groups, including a named poller and optional per-poll-group iobuf cache.
- Provides pause/resume for poll-group pollers.
- Dispatches poll-group add/remove/poll and qpair/request operations into the selected transport ops table.
- Initializes default transport opts, then invokes transport-specific defaults.
- Allocates, queues, aborts, and frees request data buffers from SPDK iobuf, including stripped DIF buffers.

Important behavior:
- `opts_size` controls which fields are copied, preserving compatibility with callers compiled against older `spdk_nvmf_transport_opts` layouts.
- `max_io_size` must be a power of two and at least 8 KiB when nonzero.
- `max_aq_depth` is clamped upward to the NVMf minimum.
- `kas` and `min_kato` must be nonzero; `min_kato` is rounded up to a KAS time-unit multiple.
- Per-core iobuf cache requests larger than the backing pool are reduced to half the global pool divided by core count.
- `UINT32_MAX` iobuf cache sizes are interpreted dynamically as half the pool divided by number of target poll groups, with core-count fallback.
- Listener refcounts allow multiple subsystem users to share a transport listener; only the final stop removes the concrete listener.
- When a listener is removed, subsystem listener pointers to its embedded `trid` are nulled to avoid dangling references.
- Buffer acquisition can be asynchronous only if the transport implements `req_get_buffers_done`; otherwise partial allocations are freed on `-ENOMEM`.
- Stripped DIF buffer allocation first verifies existing request iovs are block-size aligned.

Dependencies:
- Depends on `nvmf_internal.h` for target, qpair, subsystem, listener, and poll-group internals.
- Depends on public SPDK NVMf transport ops and transport opts definitions.
- Uses SPDK iobuf module/channel APIs for shared request data buffer pools.
- Uses SPDK poller, thread/channel iteration, JSON, logging, queue, utility, and DTrace/USDT helpers.

Notable risks:
- Transport ops are trusted after registration; missing required callbacks would fail later through direct dispatch or asserts.
- Listener `sock_impl` comparison assumes an existing listener string is valid when comparing repeated listen options.
- Poll-group destruction logs if the pending buffer queue is nonempty, but cleanup correctness depends on transports and request paths having drained or aborted outstanding buffer waiters.
- The struct-size static assert requires updates whenever `spdk_nvmf_transport_opts` changes.
