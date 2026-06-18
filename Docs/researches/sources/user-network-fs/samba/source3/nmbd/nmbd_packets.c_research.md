# sources/user-network-fs/samba/source3/nmbd/nmbd_packets.c

## Purpose
`nmbd_packets.c` is the central packet I/O and dispatch layer for Samba's NetBIOS name daemon. It initializes the unexpected packet side server, builds outbound NetBIOS name packets and datagram mailslot frames, queues inbound packets, validates and routes NMB requests/responses, retransmits expected-response records, and drives socket polling for all configured IPv4 broadcast, unicast, and datagram sockets.

## Important APIs, types, and functions
- `nmbd_init_packet_server` creates the `nb_packet_server` used for packets that nmbd decides not to consume directly.
- `get_nb_flags` and `set_nb_flags` encode/decode the NetBIOS flags byte used in NB resource records.
- `queue_register_name`, `queue_wins_refresh`, `queue_register_multihomed_name`, `queue_release_name`, `queue_query_name`, `queue_query_name_from_wins_server`, and `queue_node_status` are the public queuing APIs for outbound NMB operations.
- `reply_netbios_packet` constructs NMB replies for normal name service and WINS paths.
- `queue_packet`, `run_packet_queue`, `listen_for_packets`, and `send_mailslot` form the runtime event-loop boundary.

## Control flow
Outbound name-service requests start by creating a packet with a generated transaction id, opcode-specific flags, and a destination subnet or WINS server address. Successful sends are wrapped in `response_record` objects so later responses and timeouts can call operation-specific callbacks. `listen_for_packets` builds or refreshes the listen array, waits through `tevent`, reads UDP packets, suppresses duplicates, and queues each packet. `run_packet_queue` drains that queue into NMB request/response dispatch or datagram mailslot dispatch.

## State and persistence behavior
The file keeps process-local state only: `packet_queue`, `name_trn_id`, `packet_server`, `rescan_listen_set`, and static listen-array state. Persistent effects happen through called modules. Packet lifetime is controlled by `locked`; loopback paths deep-copy packets into `packet_queue`, and response records lock sent packets until removed.

## Dependencies and integration points
This code depends on `nmbd.h`, subnet globals, response-record helpers, WINS handlers, normal request handlers, browse/logon handlers, async DNS, Samba socket utilities, `tevent`, and `libsmb/unexpected`.

## Risks and edge cases
Datagram parsing uses historical SMB offset conventions and must maintain strict bounds checks. Response-record callbacks can remove records while timeout traversal is running. Loopback handling depends on correct packet deep-copy and lock semantics. WINS selection for zero unicast address currently uses only the first active WINS server/tag.

## Test signals
Use integration tests for registration/query/release, WINS registration conflicts, browser announcements, mailslot logon replies, duplicate broadcast packets, and timeout/retry behavior. Static review should focus on packet length guards and response-record ownership.
