# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_cnfg.h

MPT MPI configuration-page ABI header for adapter, port, device, RAID, LAN, and SAS topology configuration.

Key responsibilities:
- Defines generic and extended config page headers, config request/reply messages, config actions, page attributes, page types, extended page types, and page-address encodings.
- Defines manufacturing pages for chip, board, VPD, hardware settings, inquiry data, integrated RAID settings, base WWID, and product-specific data.
- Defines IO Unit and IOC pages for adapter identity, BIOS flags, GPIO, reply coalescing, EEDP, RAID volume/physical disk inventories, and enclosure processors.
- Defines SCSI port/device pages for physical capabilities, termination/scanning/init policy, negotiated/requested parameters, and domain validation controls.
- Defines Fibre Channel port/device pages for WWN/port identity, topology, speed, persistent targets, aliases, statistics, symbolic names, and attached-node data.
- Defines RAID volume and physical disk config pages, including volume status/settings, disk inquiry data, error data, hot spare pools, and multi-path physical disk paths.
- Defines LAN and inband pages.
- Defines SAS IO Unit, expander, device, and PHY extended pages for link rates, persistent mappings, discovery state, enclosure handles, SAS addresses, device handles, topology, routing, and PHY error counters.

Dependencies:
- Relies on types and SGE/version definitions from `mpi.h`.
- Some FC protocol flag macros refer to IOC port-facts protocol constants defined in `mpi_ioc.h`.

Notable risks:
- Many pages use compile-time one-element arrays with comments requiring callers to inspect `Header.PageLength` or `ExtPageLength` at runtime.
- Constants encode firmware NVRAM and topology contracts; changing values or packing would break adapter configuration.
- The file intentionally contains legacy and newer-page definitions together, so consumers must use page versions and lengths defensively.
