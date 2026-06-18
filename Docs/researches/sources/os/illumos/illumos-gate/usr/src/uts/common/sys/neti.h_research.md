# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/neti.h

Kernel netinfo and network hooks framework interface.

Key responsibilities:
- Defines netinfo version, hook family names for IPv4, IPv6, ARP, and VIONA, and hook event names for physical in/out, forwarding, loopback in/out, NIC events, and observation.
- Defines hardware checksum capability bits and helper macros querying partial checksum status.
- Defines physical/logical interface IDs, network ID, interface address selector enum, injection mode enum, packet injection request, and `net_handle_t`.
- Defines protocol provider callback table for interface name, MTU, PMTU, logical interface addresses/zones/flags, physical/logical walks, packet injection, route lookup, and checksum validation.
- Defines internal protocol, injection, instance, instance-wrapper, and per-netstack data structures with lists, refcounts, hooks, netstack IDs, zones, condition variables, and condemnation flags.
- Provides IPIF ID mapping macros.
- Declares internal initialization and netid/netstack/zone mapping helpers.
- Declares public hook event/family/hook registration, packet injection allocation/free/inject, net instance registration/notification, kstat creation/deletion, protocol register/lookup/walk/release/unregister/notification, and interface/query wrappers.

Dependencies:
- Includes inet socket types, integer types, queue/list macros, hook implementation, and netstack headers; avoids including `sys/stream.h` by forward-declaring `struct msgb`.

Notable risks:
- This is an extensible kernel plugin interface with refcounted and condemned objects; teardown must coordinate with hook callbacks.
- Packet injection path crosses protocol stacks and zones, so netid/zone mapping and address validation are critical.
