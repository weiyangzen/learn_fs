# File Research: sources/virtualization/open-iscsi/usr/flashnode.h

Defines flashnode record structures used for firmware-resident iSCSI target/session configuration.

Structures:
- `flashnode_sess_rec_t` stores target identity, CHAP credentials, discovery parent info, ISID, portal type, burst/timing parameters, CHAP indexes, TPGT, discovery flags, ordering flags, ERL, and boot target state.
- `flashnode_conn_rec_t` stores IP/redirect/link-local addresses, segment lengths, TCP window scale, sequence numbers, ports, IPv6 flow label, digest and TCP behavior flags, TOS/traffic class.
- `flashnode_rec` combines list linkage, transport name, session record, and one connection record.

Exports flat printing, flashnode logout by SID, and netlink config building.
