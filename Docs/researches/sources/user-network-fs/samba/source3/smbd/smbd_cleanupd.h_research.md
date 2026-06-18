# sources/user-network-fs/samba/source3/smbd/smbd_cleanupd.h

## Purpose
Declares the async cleanup daemon API used by smbd process-management code.

## Important APIs, Types, and Functions
Exports `smbd_cleanupd_send(TALLOC_CTX *, tevent_context *, messaging_context *, pid_t parent_pid)` and `smbd_cleanupd_recv(struct tevent_req *)`. Includes `replace.h`, `tevent.h`, and `messages.h`.

## Control Flow
Callers start cleanup handling by invoking `send`, keep the request alive while the daemon should process messages, and call `recv` after request completion, normally after shutdown.

## State and Persistence
No direct state. The implementation retains parent PID in request state and uses cleanupdb/messaging state outside the header.

## Dependencies and Integration Points
The signature ties cleanupd to Samba's tevent request model and messaging subsystem. It is integrated wherever the parent smbd starts helper daemons or message-driven maintenance tasks.

## Risks
Consumers must preserve the returned request lifetime because message registrations use it as private data. Calling `recv` before completion follows tevent semantics and should be avoided.

## Test Signals
Compile consumers against the send/recv signatures and exercise start/shutdown paths through the implementation.
