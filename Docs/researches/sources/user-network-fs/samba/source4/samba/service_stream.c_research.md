<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.c -->
# sources/user-network-fs/samba/source4/samba/service_stream.c

## Purpose

`service_stream.c` provides reusable helpers for stream-oriented Samba services: listener setup, accept dispatch through process models, connection object creation, IO dispatch, and connection termination.

## Important APIs, Types, and Functions

`struct stream_socket` stores listener state. Public functions include `stream_setup_socket()`, `stream_new_connection_merge()`, `stream_terminate_connection()`, `stream_io_handler_fde()`, `stream_io_handler_callback()`, and `stream_connection_set_title()`. Static helpers include `stream_accept_handler()`, `stream_new_connection()`, and `stream_io_handler()`.

## Control Flow

`stream_setup_socket()` creates a socket, resolves/binds/listens on IP or non-IP addresses, registers a tevent fd, and stores model/service ops. When readable, `stream_accept_handler()` asks the selected process model to accept and possibly fork. `stream_new_connection()` builds `stream_connection`, checks host access, registers fd and messaging contexts, records addresses, sets a title, enables reads, and calls the service's accept hook. IO events call send or receive handlers. Termination defers if inside an IO callback, otherwise frees fd, messaging, connection, and calls the model's `terminate_connection()`.

## State and Persistence Behavior

Listener and connection state is talloc-owned. Connections have per-server IDs, local/remote addresses, optional tstream/session info, and process-context pointers. No durable state is written except effects of downstream services.

## Dependencies and Integration Points

It integrates socket backends, tevent fd events, process models, imessaging, loadparm host allow/deny, cluster IDs, tsocket formatting, and stream server ops.

## Risks and Edge Cases

Termination during a callback is intentionally deferred to avoid use-after-free. Dynamic RPC port allocation iterates the configured low/high range. Socket ownership is split between tevent and socket flags, so close semantics are delicate. Access checks use the default service's host allow/deny lists.

## Test Signals

Tests should cover IP and Unix listener setup, dynamic port assignment, socket option failures, host access denial, accept under each process model, deferred termination from recv/send handlers, merged connections, and process-title updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service_stream.c -->
