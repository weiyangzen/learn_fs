# File Research: sources/virtualization/open-iscsi/usr/config.h

Defines core open-iscsi configuration records for sessions, connections, discovery, interfaces, and nodes.

Important groups:
- Authentication config stores auth method, outbound/inbound usernames and passwords, and CHAP algorithm list.
- Timeout configs split connection, session replacement, and error recovery timers.
- TCP config stores window/TOS/congestion control.
- Operational configs store iSCSI digest, ordering, burst, R2T, ERL, and connection limits.
- `iface_rec_t` is large and covers network addressing, VLAN, IPv6 autoconf, TCP knobs, digest options, offload parameters, boot aliases, and initiator naming.
- `node_rec_t` combines target identity, session config, one connection record, iface binding, and discovery source.
- `discovery_rec_t` stores SendTargets or iSNS discovery configuration.

This header is a central data contract across idbm, discovery, login, firmware boot, flashnode, and transport code.
