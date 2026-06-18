# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_client_priv.h

## Role

Private MAC client API for GLDv3 stack components only: dld, dls, aggr, and softmac.

## Structure

Under `_KERNEL`, declares APIs for RX bypass, MAC info, start/stop/ioctl/link, resources, devinfo/driver access, capability/SAP/header operations, perimeter entry/exit, VNIC VLAN handling, polling, flow management, quiesce/restart, hardware ring/group operations, hardware VLAN/promisc, upper MAC setup, exclusivity, ring availability, interrupt CPU assignment, property get/set/info, and pseudo-ring stats.

## Dependencies And Consumers

Includes `sys/mac.h` and `sys/mac_flow.h`. Intended consumers are private GLDv3 implementation modules, not arbitrary drivers.

## Important Details

`MAC_PERIM_HELD()` checks perimeter ownership only in DEBUG builds. Several APIs expose low-level hardware ring passthrough and classifier manipulation, so misuse outside the MAC stack could violate synchronization/resource assumptions.

## Research Notes

Read completely: 208 lines, 8124 bytes.
