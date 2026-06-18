# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_impl.h

## Role

Primary private MAC Services implementation header. It defines core MAC provider state, callback list infrastructure, rings/groups, addresses, registered MAC instance layout, resource accounting, property-info state, and many internal MAC routines.

## Structure

- Defines MAC private/minor ranges, margin/MTU request nodes, generic chains, callback list structures/macros, mactype registration state, group/ring state enums, `mac_ring_t`, ring ref macros, group-client and `mac_group_t`.
- Defines factory/multicast/address/VLAN structures, global MAC instance registry variables, and the large `mac_impl_t` with locks, identity, driver callbacks, link state, perimeter, notify callbacks, ring groups/capabilities, transceiver/LED state, address lists, flow table, clients, SDU/margin/MTU, factory addresses, promiscuous callbacks, resources, minor/open refs, legacy/share/bridge state, and DEBUG perimeter stack.
- Defines default group macros, ring/group resource accounting macros, MAC state flags, callback aliases, perimeter handle encode/decode, property info flags/state, protection helper, and extensive internal function prototypes for MAC core, callbacks, broadcast/multicast, rings/groups, flows, datapath, VLAN tags, Tx/Rx, shares, perimeter, notifications, protection, resources, bridging, transceivers, LEDs, direct RX, and broadcast groups.

## Dependencies And Consumers

Includes cpupart, modhash, MAC client/provider, note, AVL, network interface, MAC flow implementation, IPv6, and packet attribute headers. Consumed only by MAC Services implementation and closely related GLDv3 internals.

## Important Details

The header documents field protection discipline: write-once, serializer-protected, and lock-protected members. `MAC_DEFAULT_TX_GROUP(mip)` points one past `mi_tx_groups + mi_tx_group_count`, which reflects the local convention for default Tx group placement and must match allocation logic. The perimeter handle encodes a low-bit `need_close` flag into an aligned pointer.

## Research Notes

Read completely: 948 lines, 31646 bytes.
