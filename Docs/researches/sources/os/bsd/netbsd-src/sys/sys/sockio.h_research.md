# File Research: sources/os/bsd/netbsd-src/sys/sys/sockio.h

Read completely: 158 lines.

This header defines socket and network-interface ioctl command numbers. It covers socket high/low watermarks, OOB mark, process group, SCTP peeloff, route add/delete, interface address/flags/broadcast/netmask/metric/configuration, aliases, multicast, media, generic driver data, tunnel physical addresses, MTU, clone interface management, data-link type, capabilities, CARP, interface data/stat zeroing, link strings, ether capabilities, interface index/description, MBIM/UMB, pfsync, and neighbor info.

Risks: command numbers are persistent ABI. Several ioctl numbers are intentionally reused for get/set pairs or reserved by subsystem-specific headers, so new additions must avoid collisions.
