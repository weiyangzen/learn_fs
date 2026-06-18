# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld.h

## Scope

Complete file read, 466 lines. This header defines the Data-Link Driver ioctl ABI plus kernel-only DLD capability and entry point interfaces.

## Public Surface

The shared ioctl surface includes DLD module metadata, driver property names, ioctl command numbers, and structures for:

- link attributes, VLAN attributes, physical attributes
- secure object set/get/unset
- VLAN create/delete
- door server state
- link rename and zone id data
- autopush configuration
- MAC address enumeration
- flow add/remove/modify/walk and flow info
- usage logging
- MAC property get/set
- hardware group enumeration
- transceiver get/read
- LED get/set

The file uses packing pragmas on platforms where 64-bit and 32-bit long-long alignment differs, preserving ioctl layout compatibility.

Under `_KERNEL`, it defines DLD capability constants, enable/disable/query values, `dld_capab_func_t`, direct transmit/receive capability structure, polling capability structure, LSO capability flags/structure, driver entry point prototypes, stream open/close/private hooks, autopush, and flow management functions.

## Behavior And Integration

Userland tools and kernel modules use the ioctl structures to control GLDv3 data links through `/dev/dld`. Kernel IP/DLD integration uses capability negotiation for direct paths, polling/softring behavior, and LSO.

## Dependencies And Invariants

The header depends on `sys/mac.h`, `sys/mac_flow.h`, STREAMS, DLD ioctl command macros from `dld_ioc.h`, and datalink identifiers. The comment explicitly requires identical structure layout and size in ILP32 and LP64.

## Risks

Flexible trailing data in `dld_ioc_macprop_t.pr_val[1]` requires careful allocation and copyin/out sizing. Ioctl command slots are historically reserved or removed; reusing them can break compatibility. Function pointers in capability structures are stored as `uintptr_t`, so consumers must cast carefully.
