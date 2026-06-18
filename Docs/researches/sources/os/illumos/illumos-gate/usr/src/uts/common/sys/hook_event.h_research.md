# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hook_event.h

## Role

`hook_event.h` defines event payloads passed through the network hook framework, including packet events, NIC state events, and IP observability packet metadata.

## Key Interfaces and Data

- `hook_pkt_event_t` carries packet hook data: protocol handle, inbound/outbound physical interfaces, protocol header pointer, pointer to mblk chain pointer, mblk containing header, flags, and reserved slots.
- Packet flags include multicast and broadcast.
- `nic_event_t` enumerates NIC events: plumb, unplumb, up/down, address change, logical interface up/down, and ifindex change.
- `hook_nic_event_t` carries protocol, physical interface, logical interface, event type, optional event data, and data length.
- `hook_nic_event_int_t` adds netstack ID for IP internal queued events.
- `hook_pkt_observe_t` mirrors externally visible `dl_ipnetinfo_t` ordering/size for version, address family, hook type, packet length, interface indexes, source/destination zones, then internal packet/context pointers.
- `ipobs_hook_type_t` enumerates inbound, outbound, and local IP observability hooks.

## Dependencies and Use

The header includes `sys/neti.h` and `sys/hook.h` and forward-declares `struct msgb` to avoid pulling in STREAMS headers.

## Research Notes

The observability structure has an explicit layout compatibility requirement with `dl_ipnetinfo_t`, making field order part of the ABI.
