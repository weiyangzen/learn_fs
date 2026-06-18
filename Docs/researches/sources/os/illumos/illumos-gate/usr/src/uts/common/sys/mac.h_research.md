# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac.h

## Role

Core MAC Services public/kernel header. It defines common datalink types, properties, statistics, plugin interfaces, resource callbacks, MAC type registration, hardware emulation flags, and core MAC provider/client-facing kernel functions.

## Structure

- Defines MAC module info/version, opaque handles, datalink ID constants, link state/duplex/flow-control/FEC/tag-mode enums, property range types, address limits, secondary address container, log types, and public property IDs.
- Kernel section defines MAC and MAC-type statistic ranges, common statistics, immutable `mac_info_t`, VNIC/aggr capabilities, bridge callbacks, notification types, RX/resource callback types, interrupt/resource structures, address/header info, direct RX callback, resource callbacks, and MAC-type plugin ops.
- Defines ndd mapping and stat info structures, `mactype_register_t`, packet hardware-emulation flags, driver interface functions, mactype register/unregister functions, log usage, VNIC helpers, packet hash flags, bridge linkage, and TRILL snoop hook.

## Dependencies And Consumers

Includes `sys/types.h`; kernel builds include DDI definitions. Consumers are GLDv3 MAC providers, MAC-type plugins, datalink/VNIC/aggr/bridge code, and networking subsystems.

## Important Details

Property and statistic enums warn to append only and not reorder, preserving ABI/semantic numbering. Optional MAC-type callbacks are negotiated through `mtops_ops` bits to preserve plugin compatibility.

## Research Notes

Read completely: 758 lines, 21739 bytes.
