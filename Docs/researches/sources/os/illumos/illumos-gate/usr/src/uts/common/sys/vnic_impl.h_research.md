# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic_impl.h

## Role

`vnic_impl.h` defines kernel-private VNIC state and VNIC device-management entry points.

## Key Structures

`vnic_t` stores:
- VNIC datalink ID and enabled bit,
- MAC handles for the VNIC and lower link,
- primary and secondary MAC client/unicast handles,
- margin, factory slot, address type, address bytes and length,
- VLAN ID, VRID, address family, force flag,
- lower link ID and MAC notify handle,
- transmit checksum flags, LSO capability, MTU, and link state.

Convenience macros identify the primary MAC client and unicast handles.

## Functions

The header declares:
- `vnic_dev_create()`
- `vnic_dev_modify()`
- `vnic_dev_delete()`
- `vnic_dev_init()`
- `vnic_dev_fini()`
- `vnic_dev_count()`
- `vnic_get_dip()`
- `vnic_info()`

## Research Notes

This is internal to the VNIC driver/control plane. It combines MAC-provider state, MAC-client state, datalink IDs, and user-visible configuration from `vnic.h`.
