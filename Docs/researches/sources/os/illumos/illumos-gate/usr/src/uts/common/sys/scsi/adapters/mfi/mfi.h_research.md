# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi.h

## Role

Core MegaRAID Firmware Interface header shared by illumos MFI-compatible drivers. It defines firmware commands, statuses, DCMD opcodes, packed command frames, controller properties/info, and patrol-read structures.

## Key Elements

- Forward-declares all major MFI protocol structures from this and companion headers.
- Defines controller limits for logical and physical drives.
- Defines firmware init/reset flags and common reset flag combination.
- Defines frame flags for reply queue posting, 64-bit SGL/sense, data direction, and IEEE SGL format.
- Defines MFI command opcodes for init, logical drive read/write/SCSI I/O, physical drive SCSI I/O, DCMD, abort, SMP, STP, and invalid command.
- Defines many firmware completion statuses.
- Defines DCMD opcodes for controller info/properties/events/shutdown/time/flash, patrol read, physical-drive list/info/state/rebuild/clear/locate, logical-drive map/list/info/property/delete, config read/add/clear/spare/foreign config, and BBU operations.
- Defines BBU type, patrol-read state/mode, and physical/logical-drive query types.
- Packed protocol types:
  `mfi_cap_t`, `mfi_sgl_t`, `mfi_header_t`, init/I/O/passthrough/DCMD/abort payloads, and 64-byte `mfi_frame_t`.
- `mfi_ctrl_props_t` models controller tunables and feature toggles.
- `mfi_image_comp_t` models firmware image component metadata.
- `mfi_ctrl_info_t` is a large 0x800-byte packed controller information block covering PCI identity, host/device interfaces, firmware images, drive counts, memory/error counters, RAID capabilities, adapter options, controller properties, package version, physical-drive limits, feature options, temperatures, cluster state, and later adapter capability bitsets.
- `mfi_pr_properties_t` and `mfi_pr_status_t` describe patrol-read configuration and state.
- `mfi_progress_t` stores progress and elapsed time.

## Dependencies and Coupling

Includes bitfield and debug support, uses packed firmware layouts, and relies on `CTASSERT` to enforce expected wire sizes and offsets.

## Research Notes

This file is a hardware/firmware ABI map. The compile-time assertions are critical: frame size, controller info size, and property block sizes must match firmware expectations exactly.
