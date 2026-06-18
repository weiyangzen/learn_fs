# sources/user-network-fs/samba/source3/torture/msg_source.c

## Purpose
`msg_source.c` is a standalone message generator for Samba's internal messaging system. It repeatedly sends fixed-size `MSG_SMB_NOTIFY` buffers to a destination `server_id` supplied on the command line.

## Important APIs, types, and functions
`struct source_state` stores the tevent context, messaging context, message type, interval, and destination id. `source_send()` starts a recurring wakeup request, `source_waited()` sends one message and arms the next timer, and `source_recv()` returns any stored Unix error. `main()` handles argument parsing, context setup, id parsing, and polling.

## Control flow
After loading config and initializing messaging, `main()` gets its own id to provide the correct virtual node number, parses the destination with `server_id_from_string`, starts a `source_send` loop with a 10 ms interval, and polls the request. Each timer callback sends a 200-byte zeroed buffer via `messaging_send_buf`.

## State and persistence behavior
The program has no durable state. In-memory state consists of the active tevent request and destination id. It emits traffic into Samba's local messaging subsystem.

## Dependencies and integration points
It is built as `msg_source` and is designed to target the id printed by `msg_sink`. It depends on `messages.h`, `server_id` helpers, `tevent_wakeup_send`, and Samba config loading.

## Risks and test signals
Invalid destination ids are rejected up front. The send return value is not checked in the callback, so the primary observable signal is whether the sink count increases. It is useful for load/liveness testing and less useful for precise delivery accounting.
