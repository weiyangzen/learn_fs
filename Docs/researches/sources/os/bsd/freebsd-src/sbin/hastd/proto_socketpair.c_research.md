# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_socketpair.c

Read completely: 235 lines.

This file implements a `socketpair://` protocol backend for local in-process or parent/child communication.

Key responsibilities:
- Creates a UNIX `SOCK_STREAM` socketpair for client setup.
- Infers side lazily: first send selects the client side, first receive selects the server side.
- Closes the unused end after side selection.
- Delegates data and descriptor send/receive to `proto_common_send()` and `proto_common_recv()`.
- Returns the active descriptor for select/control logic.
- Closes both descriptors if side is still undefined, or the active descriptor for a selected side.
- Registers the backend as non-default under protocol name `socketpair`.

Important interactions:
- Used by `hastd_primary()` for control, event, and connection request channels.
- Used by `proto_connection_send()`/`recv()` paths to pass TCP descriptors between parent and child.

Reliability notes:
- Side selection is implicit and order-dependent; the caller must perform the initial direction-declaration send/recv consistently.
- The backend has no address matching or address rendering because it is local-only.
