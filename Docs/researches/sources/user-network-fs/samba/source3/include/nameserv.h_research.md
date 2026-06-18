# sources/user-network-fs/samba/source3/include/nameserv.h

## Purpose
`nameserv.h` defines NetBIOS Name Service and datagram protocol constants and packet layouts used by nmbd and related browser/name-query code. It maps RFC1001/RFC1002 fields, WINS record flags, browser mailslot identifiers, and Samba packet queue structures.

## Important APIs, Types, And Control Flow
Important definitions include name service opcodes, question/resource record types and classes, NetBIOS node flags, WINS state/type/location/static bits, name-state helper macros, error codes, refresh timers, mailslot names, node and packet type enums, NetBIOS name buffers (`nstring`, `unstring`), `struct nmb_name`, node status records, resource records, NMB packets, datagram packets, and `struct packet_struct` queue nodes. Browser announcement message IDs are also defined.

## State And Persistence
The header describes packet and queue state, not persistent storage. Runtime state includes packet linked lists with lock flags, source/destination sockets, timestamps, IP/port metadata, and embedded decoded NMB or datagram bodies. WINS flags represent persistent or replicated name database state elsewhere, including active, released, tombstoned, deleted, local/remote, dynamic/static, and node-type attributes.

## Dependencies And Integration Points
It depends on basic network types such as `struct in_addr` and Samba boolean/string typedefs. It integrates with name registration, release, refresh, WINS server logic, browse list announcements, mailslot datagrams, node status queries, and packet send/receive queues.

## Risks And Test Signals
Risks include wire-format size limits (`MAX_DGRAM_SIZE`), ambiguity between refresh opcodes 8 and 9, malformed flag combinations, fixed scope/name buffer truncation, queue locking races, and WINS state mask mistakes. Test signals include RFC1002 packet encode/decode, name query/status/register/refresh/release paths, WINS active/released/tombstoned transitions, browser mailslot parsing, datagram fragmentation flags, max datagram rejection, and multi-node-type registration behavior.
