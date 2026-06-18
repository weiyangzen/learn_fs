# sources/user-network-fs/samba/source3/torture/msg_sink.c

## Purpose
`msg_sink.c` is a standalone messaging throughput sink. It prints its `server_id`, continuously receives `MSG_SMB_NOTIFY` messages, and periodically prints the number received.

## Important APIs, types, and functions
The file uses tevent request patterns with `sink_send`/`sink_done`/`sink_recv`, `prcount_send`/`prcount_waited`/`prcount_recv`, and `msgcount_send`/`msgcount_sunk`/`msgcount_printed`/`msgcount_recv`. `struct sink_state`, `struct prcount_state`, and `struct msgcount_state` hold event loop, messaging context, interval, and count pointers.

## Control flow
`main()` loads global Samba configuration, initializes a tevent context and messaging context, prints the current `server_id`, starts `msgcount_send`, then polls forever. `msgcount_send` starts two independent child requests: one recurring `messaging_read_send` chain that increments the count per message, and one recurring timer that prints the count each second.

## State and persistence behavior
The only state is in memory: the messaging context registration/state, the count, and active tevent requests. It does not write durable files, but it participates in Samba's messaging transport and therefore depends on local messaging socket/TDB infrastructure.

## Dependencies and integration points
It includes `messages.h`, `server_id.h`, and `tevent_unix.h`, and is built as the `msg_sink` binary. It pairs naturally with `msg_source.c`, which accepts the printed destination id.

## Risks and test signals
The request loops are intentionally non-terminating unless an error occurs. A stalled count, `messaging_read_recv` error, or timer allocation failure points to messaging delivery, event-loop, or local messaging database problems. It is a throughput and liveness tool rather than a pass/fail unit test.
