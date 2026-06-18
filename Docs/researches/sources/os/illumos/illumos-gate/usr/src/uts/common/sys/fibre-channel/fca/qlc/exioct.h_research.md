# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioct.h

This large header defines QLogic SAN/device-management external ioctl ABI structures and command namespaces used by management tools for the `qlc` Fibre Channel adapter driver.

Key contents:
- External ABI version `EXT_VERSION`.
- Generic constants for signature, WWN, serial, port ID, string, SCSI CDB, MAC address, and address-mode sizes.
- OS-dependent limits imported from `exioctso.h`.
- Main ioctl envelope `EXT_IOCTL`, including signature, request/response addresses, vendor data, status/detail status, request/response lengths, address mode, version, subcode, instance, HBA selector, and vendor-specific status.
- Status and detail-status codes for success, busy, pending, invalid parameters, overruns/underruns, device/HBA readiness, mailbox/SCSI status, unsupported subcodes/versions, queue full, and VP index errors.
- DeviceControl/ioctl command aliases for query, FCCT/ELS/SCSI passthrough, AEN registration/retrieval, RNID, host/RISC/NVRAM/option ROM/VPD/flash operations, fcache, SFP, PCI data, firmware traces, vports, reset, I2C, dump, SerDes, VF state, flash update capabilities, and BB_CR data.
- Extensive subcode definitions for query/get/set operations, SCSI passthrough, NVRAM scope, vport commands, flash access, firmware reset, I2C temperature, dump, SerDes, and flash-update capabilities.
- Query/result structures for HBA node, HBA port, FC4 statistics, loopback request/response, discovered ports/targets/LUNs, SCSI/FC/destination addresses, port statistics, driver properties, firmware properties, chip properties, CNA port properties, adapter region versions, RNID requests/responses, SCSI and FC-SCSI passthrough, AEN registration/events, beacon control, LUN bitmasks, device database entries/lists, target swap data, IIDMA port parameters, PCI option-ROM header/data, Menlo/Mercury firmware management, virtual port IDs/params/info, board temperature, SerDes registers, VF state, FCF list, resource counts, firmware FCE trace, ELS passthrough request, flash update capabilities, and BB_CR data.
- Macros for LUN bitmask manipulation and many FC/FCoE/port-speed/device-type constants.

Dependencies:
- Includes `exioctso.h`.
- Uses fixed QLogic typedef aliases such as `UINT8`, `UINT16`, `UINT32`, `UINT64`, `INT32`, and `INT64`.

Research notes:
- This is a management ABI, not just an internal header. Structure sizes and fields are annotated and must remain compatible with user tools.
- Several structures use embedded addresses as integer fields because ioctl callers may be 32-bit or 64-bit, controlled by `AddrMode`.
- The file spans classic Fibre Channel, FCoE/CNA, Menlo/Mercury management, virtual ports, flash/NVRAM, diagnostics, firmware traces, and physical-layer controls.
