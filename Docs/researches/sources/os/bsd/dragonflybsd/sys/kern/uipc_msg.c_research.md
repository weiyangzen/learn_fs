# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_msg.c

## Summary
Socket protocol-request message wrapper layer. It marshals `pr_usrreqs` and protocol control operations through LWKT/netisr message ports, with direct, synchronous, and asynchronous variants.

## Main Responsibilities
- Wraps socket protocol operations: abort, accept, attach, bind, connect, connect2, detach, disconnect, listen, peeraddr, rcvd, rcvoob, send, sense, shutdown, sockaddr, ctloutput, ctlinput.
- Provides direct-call variants for cases already on the owning CPU/port.
- Provides async fast paths for attach, connect, send, and received-notification operations.
- Implements predicate socket-buffer notification messages and abort handling.
- Manages async `pru_rcvd` message reply/drop races.

## Important Behavior
Synchronous wrappers build stack `netmsg_*` structures and call `lwkt_domsg` on `so->so_port`. Async wrappers allocate or embed messages, copy transient sockaddr data when needed, optionally hold threads according to protocol flags, and dispatch on current CPU when already on the target netisr port.

Control input uses `pr_ctlport` to identify the correct protocol port before issuing synchronous messages. Direct control input only executes if the selected CPU matches current CPU or is wildcard.

Predicate notification queues messages on send/receive socket buffers when the predicate is not yet true; aborts are requeued to the target CPU to interlock with reply races.

## Risks
This layer is sensitive to message lifetime and CPU/port ownership. Async send embeds the message in the mbuf header, so the mbuf must remain valid until protocol handling. `so_async_rcvd_drop` may sleep/retry around `MSGF_DONE` races and tracks them with `async_rcvd_drop_race`.
