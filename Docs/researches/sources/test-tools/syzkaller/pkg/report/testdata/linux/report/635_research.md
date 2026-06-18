# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/635

## Purpose
This fixture covers a KMSAN uninitialized-value report in `sctp_epaddr_lookup_transport`.

## Important APIs, types, and functions
Key frames include `sctp_epaddr_lookup_transport`, `sctp_endpoint_bh_rcv`, `sctp_inq_push`, `sctp_rcv`, `sctp4_rcv`, `ip_protocol_deliver_rcu`, `ip_local_deliver`, `ip_rcv`, `__netif_receive_skb`, `process_backlog`, and `net_rx_action`.

## Control flow
An SCTP packet is processed in softirq context; address initialization leaves a local `src` value uninitialized, and lookup later consumes it.

## State and persistence behavior
The log persists origin storage in `sctp_init_addrs`, local variable metadata, CPU/task context, and KMSAN type.

## Dependencies and integration points
It integrates network softirq stack parsing, SCTP protocol handling, and KMSAN origin extraction.

## Risks and test signals
The parser must classify this as `KMSAN-UNINIT-VALUE` and title it after `sctp_epaddr_lookup_transport`, not generic IP receive helpers.
