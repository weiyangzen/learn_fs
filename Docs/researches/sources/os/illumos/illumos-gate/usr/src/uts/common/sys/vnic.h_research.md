# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic.h

## Role

`vnic.h` defines the public ioctl ABI for creating, deleting, inspecting, and modifying virtual NICs.

## Key Interfaces

Diagnostic codes in `vnic_ioc_diag_t` describe extended failure reasons such as duplicate or invalid MAC addresses, invalid factory slots, unsupported factory addresses, invalid prefixes/margins, missing hardware rings, and invalid MTU.

`vnic_mac_addr_type_t` describes how a VNIC address is chosen:
- fixed,
- random,
- factory,
- auto,
- primary,
- VRID-derived,
- unknown.

Ioctl structures:
- `vnic_ioc_create_t` includes VNIC ID, lower link ID, MAC type/address/prefix/slot, VLAN ID, VRID, address family, status, creation flags, diagnostic code, and MAC resource properties.
- `vnic_ioc_delete_t` identifies a VNIC to delete.
- `vnic_info_t` reports configured VNIC properties.
- `vnic_ioc_modify_t` supports changing MAC address and/or resource controls.

Creation flags include duplicate-check bypass, anchor creation, and forced VLAN-based VNIC creation without margin checking.

## ABI Notes

The file uses `#pragma pack(4)` under mixed 64-bit/32-bit long-long alignment conditions to preserve ioctl ABI compatibility.

## Research Notes

This header sits at the datalink/MAC management boundary. The structures include both administrative inputs and diagnostic outputs, so callers should inspect both errno and `vc_diag`/`vm_diag` style fields.
