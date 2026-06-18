# File Research: sources/os/linux/linux/fs/smb/smbdirect/listen.c

Implements the listener-side RDMA CM accept front-end. It binds an SMB Direct socket into listening mode, receives RDMA connect requests, validates device/protocol/backlog constraints, creates accepting child sockets, and hands them to `accept.c` for RDMA accept and SMB Direct negotiation.

Key entry points:
- `smbdirect_socket_listen()` validates backlog and socket state, switches status to `LISTENING`, installs `smbdirect_listen_rdma_event_handler()`, sets expected event to `RDMA_CM_EVENT_CONNECT_REQUEST`, and calls `rdma_listen()`.
- `smbdirect_listen_rdma_event_handler()` handles RDMA CM events for the listening CM ID. On connect requests it detaches the new CM ID from the listener context before processing and delegates to `smbdirect_listen_connect_request()`.
- `smbdirect_listen_connect_request()` validates FRWR support and optional IB/iWARP restrictions, checks pending plus ready child counts against backlog, creates an accepting socket around the new RDMA CM ID, copies listener logging/parameters/kernel settings, adds the child to the listener pending queue, and calls `smbdirect_accept_connect_request()`.

Important state and invariants:
- `listen.backlog == -1` means the socket was never a listener; valid listener backlog is always positive.
- Listener child sockets move from `listen.pending` to `listen.ready` in `accept.c` after SMB Direct negotiate request parsing succeeds.
- Backlog accounting considers both pending and ready children.
- On failure before ownership transfer is complete, the new RDMA CM ID is left for the caller/RDMA core to destroy; the child socket clears `ib.dev` and `rdma.cm_id` before release in that path.
- The temporary `smbdirect_new_rdma_event_handler()` is a guard that should never perform real work; it catches unexpected events before the accepting socket installs its handler.

Dependencies:
- Uses `socket.c` creation/configuration/release helpers.
- Uses `accept.c` for server-side connection acceptance and negotiation.
- Uses `devices/socket.c` FRWR and protocol checks.

Maintenance notes:
- The listener RDMA handler runs under the RDMA CM handler mutex and assumes it may sleep; this matters because child socket setup can allocate memory.
- The backlog check currently uses `>` rather than `>=`, allowing exactly backlog plus possibly one depending on combined counts; preserve or revisit deliberately if changing accept queue semantics.
