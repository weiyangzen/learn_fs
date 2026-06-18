# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client.h

## Role

Kernel MAC client API header for consumers that open MAC handles, add addresses, receive/transmit packets, manage promiscuous callbacks, notifications, resources, and hardware emulation.

## Structure

Defines opaque client/unicast/promisc/perimeter handles, Tx notify cookie/callback, diagnostic enum, ring request constants, promiscuous types, unicast/open/close/promisc/Tx flags, and a broad set of `mac_client_*`, unicast, multicast, rx, tx, notify, stat, primary address, factory address, resource, bridge, share, MTU, ring, and hardware-emulation prototypes.

## Dependencies And Consumers

Includes `sys/mac.h` and `sys/mac_flow.h`; all substantive declarations are under `_KERNEL`. Consumers include IP, DLS, VNIC, aggregation, bridging, and other kernel clients of MAC Services.

## Important Details

Ring constants distinguish "none" from "don't care". Unicast flags control duplicate checks, primary/VNIC roles, hardware classification, VLAN tag/strip behavior, and TX VID checks. `mac_tx()` returns a cookie that can later be tested for flow blockage.

## Research Notes

Read completely: 212 lines, 7361 bytes.
