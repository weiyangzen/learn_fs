# File Research: sources/virtualization/libnbd/lib/internal.h

Private internal contract for libnbd hand-written code and generated state-machine code.

Major definitions:
- GCC hot-path helpers `unlikely` and `if_debug`.
- `MAX_REQUEST_SIZE` set to 64 MiB.
- Vector types for metadata contexts, uint32 lists, and close callbacks.
- `struct command_cb`: callback union for extents, reads, lists, contexts, and completion.
- `struct nbd_handle`: central state object containing configuration, negotiated state, transport, buffers, command queues, state-machine state, subprocess/TCP/socket-activation data, metadata state, stats, and strictness.
- `struct socket_ops` and `struct socket`: abstraction over plain sockets and TLS-wrapped sockets.
- `struct command`: queued command object with flags/type/cookie/offset/count/data/callback/error tracking.
- `struct execvpe`: precomputed fork-safe exec context.

Macros:
- Callback null/test/call/free helpers.
- `debug`, `debug_direct`, and `set_error`.
- State access macros for generated and hand-written code.
- `NBD_INTERNAL_FORK_SAFE_ASSERT`.

Declared internal APIs:
- Command retirement, connection wait, TLS session/handshake helpers, debug/error helpers, flag setters, state predicates, option cleanup, protocol mapping, command queuing, socket creation, generated state-machine hooks, utility and fork-safe exec helpers.

Interactions:
- Includes public `libnbd.h`, local `nbd-protocol.h`, generated `states.h` and `unlocked.h`, byte-swapping, and string vector helpers.

Research notes:
- This header reveals the full architecture: one locked handle, generated state transitions, pluggable socket ops, and linked-list command queues.
- Public state is atomic and distinct from internal current state.
