# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_cfg.c

IKE configuration mode transaction implementation.

It defines the transaction exchange payload script and initiator/responder step tables for SET/ACK and REQUEST/REPLY mode. The initiator send path builds configuration attribute payloads from peer-ID-derived config sections, either sending configured address/netmask/DNS/WINS/DHCP/lifetime values or requesting attributes listed in configuration.

Receive paths verify phase-2 HASH payloads when needed, check transaction IDs and message types, decode attributes into the exchange's `ie->attrs` list, mark attribute payloads handled, and log ACK/REPLY/SET semantics. The responder send path chooses the peer identity, encodes requested attributes from local config, emits ACK or REPLY payloads, and finalizes HASH protection for phase-2 transaction exchanges.

Attribute encoding supports IPv4/IPv6 address, netmask, subnet, DHCP, DNS, NBNS, address expiry, application version, and supported-attributes shells. Unsupported/private/future attributes are ignored or rejected according to type range, and ACK responses include only attributes marked as used.
