# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_cnfg.h

## Purpose
Defines the Broadcom/LSI/Avago Fusion-MPT MPI v2.x configuration-message ABI and the associated firmware configuration page layouts used by illumos MPI-capable SCSI/SAS/PCIe adapter drivers. It maps firmware configuration actions, page headers, page-address formats, page version constants, and a large set of fixed wire-format structures for controller, manufacturing, BIOS, RAID, SAS, Ethernet, and MPI v2.6 PCIe/NVMe-related configuration pages.

## Main Interfaces
- Common config framing:
  - `MPI2_CONFIG_PAGE_HEADER`
  - `MPI2_CONFIG_PAGE_HEADER_UNION`
  - `MPI2_CONFIG_EXTENDED_PAGE_HEADER`
  - `MPI2_CONFIG_EXT_PAGE_HEADER_UNION`
  - page attribute/type constants for IO Unit, IOC, BIOS, RAID volume, manufacturing, RAID physical disk, and extended pages
  - extended page type constants for SAS IO Unit, SAS Expander, SAS Device, SAS PHY, Log, Enclosure, RAID Configuration, Driver Mapping, SAS Port, Ethernet, Extended Manufacturing, PCIe IO Unit, PCIe Switch, PCIe Device, and PCIe Link
- Page-address encodings:
  - RAID volume and RAID physical disk address forms
  - SAS expander, device, PHY, port, enclosure address forms
  - RAID configuration, driver persistent mapping, Ethernet, PCIe switch, PCIe device, and PCIe link address forms
- Config message ABI:
  - `MPI2_CONFIG_REQUEST`
  - `MPI2_CONFIG_REPLY`
  - config actions for header fetch, current/default/NVRAM read, current/NVRAM write, and changeable-mask fetch
- Manufacturing pages:
  - vendor and device ID constants for MPI v2.0, v2.5, and v2.6 SAS products
  - `MPI2_CONFIG_PAGE_MAN_0` through `MPI2_CONFIG_PAGE_MAN_7`
  - `MPI2_CONFIG_PAGE_MAN_PS` for product-specific manufacturing pages 8 through 31
  - connector, pinout, enclosure, power-save, RAID policy, disk coercion, bad-block marking, and manufacturing page-version constants
- IO Unit and IOC pages:
  - `MPI2_CONFIG_PAGE_IO_UNIT_0`, `_1`, `_3`, `_5`, `_6`, `_7`, `_8`, `_9`, `_10`
  - MPI v2.6 `MPI26_CONFIG_PAGE_IO_UNIT_11`
  - `MPI2_CONFIG_PAGE_IOC_0`, `_1`, `_6`, `_7`, `_8`
  - flags for SATA write cache, host-based discovery, fast path, RAID accelerator, power/temperature reporting, sensor thresholds, function credits, spinup groups, RAID capabilities, event masks, and persistent ID mapping
- BIOS pages:
  - `MPI2_CONFIG_PAGE_BIOS_1` through `_4`
  - boot-device selector structures for SAS WWID, enclosure/slot, device name, and adapter order
  - BIOS/UEFI registration, boot preference, removable-media behavior, adapter-order, and reassignment fields
- RAID pages:
  - `MPI2_CONFIG_PAGE_RAID_VOL_0` and `_1`
  - `MPI2_CONFIG_PAGE_RD_PDISK_0` and `_1`
  - volume state/type/status, hot-spare pools, write-cache settings, supported physical disk types, inactive reasons, physical disk state/offline/incompatible reasons, physical disk attributes, path flags, and RAID page versions
- SAS shared constants and pages:
  - common SAS link-rate, attached PHY info, PHY info, programmed link-rate, and hardware link-rate constants, including MPI v2.5 12G and MPI v2.6 22.5G values
  - SAS IO Unit pages 0, 1, 4, 5, 6, 7, 8, and 16
  - SAS Expander pages 0 and 1
  - SAS Device pages 0 and 1
  - SAS PHY pages 0 through 4
  - SAS Port page 0
  - SAS/Enclosure page 0 definitions and enclosure-level flags
- Other extended pages:
  - Log page 0 and log-entry qualifiers
  - RAID Configuration page 0 and configuration elements
  - Driver Persistent Mapping page 0
  - Ethernet pages 0 and 1
  - Extended Manufacturing product-specific page structure
- MPI v2.6 PCIe pages:
  - common PCIe negotiated link-rate constants
  - PCIe IO Unit pages 0 and 1
  - PCIe Switch pages 0 and 1
  - PCIe Device pages 0 and 2
  - PCIe Link pages 1, 2, and 3
  - PCIe/NVMe access-status values, device flags, link rates, SGL capabilities, and link-event counters/thresholds

## Dependencies And Relationships
This header depends on the core MPI type and SGE definitions from the surrounding MPI headers, especially `mpi2.h` for base integer typedefs, `MPI2_POINTER`, `MPI2_VERSION_UNION`, and `MPI2_SGE_IO_UNION`. Several comments point consumers to `mpi2_sas.h` for SAS `DeviceInfo`/controller PHY device information values and to `mpi2_pci.h` for PCIe `DeviceInfo`/controller PHY device information values.

The structures are firmware ABI records consumed by illumos MPI adapter code when issuing `MPI2_FUNCTION_CONFIG` requests, discovering topology, reading controller facts/configuration, configuring SAS/PCIe/NVMe transport behavior, handling RAID metadata, and reporting persistent mappings or enclosure state.

## Research Notes
The header identifies itself as `mpi2_cnfg.h` version `02.00.39`, with history through September 1, 2016. It explicitly distinguishes MPI v2.0/v2.5 names from MPI v2.6 additions. Many variable-length pages define array counts as small default macros, while comments instruct host code to leave those macros at one and use returned count or page-length fields at runtime. This pattern appears in manufacturing, IO Unit, RAID, SAS IO Unit, SAS PHY, PCIe IO Unit, PCIe Link, and other page families.

The file is entirely declarative but large and cross-cutting: it centralizes page-version constants, page-address forms, bit masks, shifts, states, rates, flags, and status codes. It preserves obsolete aliases and fields where required for compatibility, while adding newer MPI v2.5/v2.6 names for 12G/22.5G SAS, PCIe 16 GT/sec, fast path, SRIS, NVMe queue depth, and PCIe/NVMe initialization status.

## Notable Risks
- This is a firmware wire ABI. Structure layout, field order, reserved padding, page version values, bit positions, and page-address encodings must match controller firmware exactly.
- Variable-length page arrays must be sized from firmware-returned counts or page lengths. Treating the compile-time placeholder maximums as real limits would truncate topology, PHY, sensor, event, or path data.
- MPI v2.0, v2.5, and v2.6 features coexist. Callers must not use `MPI25` or `MPI26` structures/flags with controllers that do not advertise those revisions.
- Several sections share similarly named constants across SAS and PCIe pages. Mixing SAS link-rate, PHY-info, device-info, or access-status definitions with PCIe/NVMe pages would decode firmware data incorrectly.
- Many fields are persistent configuration or NVRAM-facing settings. Incorrect writes can alter boot order, RAID behavior, spinup policy, persistent mappings, link configuration, discovery behavior, or enclosure state.
