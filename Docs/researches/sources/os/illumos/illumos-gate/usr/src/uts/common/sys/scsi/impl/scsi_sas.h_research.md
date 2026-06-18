# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_sas.h

This header defines illumos SAS implementation interfaces, SAS PHY mapping helpers, kstat structures, protocol/link-rate constants, phy-info property names, phy-mask/depth property names, and SAS event strings.

Key definitions:
- Kernel-only phymap API:
  - create/destroy a SAS phymap
  - add/remove PHY mappings
  - look up unit addresses and private data
  - convert PHY to unit address and unit address to physical iterator
- Defines SAS PHY kstat class and documents kstat name formatting.
- Defines kstat structures for SAS port protocol stats, port stats, and PHY stats.
- Defines supported protocol bits for SSP, STP, SMP, and SATA.
- Defines SAS negotiated physical link-rate constants.
- Defines `phy-info` property names for phy ID and min/max/current link rates.
- Defines target/attached/receptacle phy-mask property names and target-port depth property.
- Defines sysevent class/subclass/type/payload strings for SAS HBA broadcasts and PHY events.

Dependencies:
- Includes `sys/types.h` and `sys/scsi/impl/usmp.h`.
- Kernel phymap APIs are gated by `_KERNEL`.

Impact:
- This is the SCSA/SAS implementation-facing header for topology mapping, stats export, properties, and event publication.

Cautions:
- Phymap callbacks return and manage unit-address private data; lifetime rules need to be followed by HBA/iport drivers.
- Link-rate values mirror SAS-2 definitions but are exposed as illumos property constants.
