# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3.h

This OFED-derived main RDSv3 header defines the protocol version, core connection/message/socket structures, transport operations, statistics, and subsystem APIs.

Core definitions:
- Protocol version is RDS 3.1, with port `18634`.
- Congestion maps are per-address bitmaps covering 65536 ports.
- Connection states are atomically tracked: down, connecting, disconnecting, up, error.
- `rdsv3_connection` stores local/remote addresses, congestion maps, send lock/generation/senders, in-flight transmit offsets, send/retrans queues, RX sequence, transport hooks/data, atomic state, reconnect timing, work items, CM lock, congestion map transfer state, unacked counters, and protocol version.
- `rdsv3_header` carries sequence, ACK, length, source/destination ports, flags, credit, checksum, and extension header space.
- Extension headers support version, RDMA completion key, and RDMA destination key/offset.
- `rdsv3_incoming`, `rdsv3_message`, and `rdsv3_notifier` define receive objects, send/receive messages, RDMA notifier delivery, refcounts, list ownership flags, and RDMA metadata.
- `rdsv3_transport` is the transport ops vector for connection allocation, connect/shutdown, transmit, congestion map transmit, RDMA transmit/MR handling, receive, CM callbacks, stats, and exit.
- `rdsv3_sock` stores socket linkage, bound/connected addresses/ports, preferred transport, cached connection, congestion state, send/receive queues, notifier queue, RDMA keys, options, credentials, and zone.

API surface:
- Bind, connection lifecycle, receive/send, congestion, stats/sysctl, threads, transport registration, message construction/extensions/checksum, RDMA, and service-console helpers.

Risk-sensitive invariants:
- Message list flags avoid lock nesting between socket and connection lists.
- Connection state transitions use atomic compare-and-swap and imply memory ordering.
- Checksum covers the RDSv3 header and treats zero checksum as acceptable.
