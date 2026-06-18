# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/spc3_types.h

## Purpose
Defines packed SPC-3/SPC-4 SCSI command, status, mode-page, diagnostic, persistent reservation, buffer, inquiry, REPORT LUNS, and NAA identifier wire structures used by illumos SCSI code.

## Main Interfaces
- `spc3_cmd_t`: broad SCSI opcode enum mapped to illumos `SCMD_*` constants and explicit numeric opcodes.
- `spc3_dev_type_t`, `sam4_status_t`, `spc4_protocol_id_t`, `naa_id_t`.
- Packed CDB/data layouts for INQUIRY, LOG SELECT/SENSE, MODE SELECT/SENSE, PERSISTENT RESERVE IN, READ/WRITE BUFFER, REQUEST SENSE, REPORT LUNS, SEND/RECEIVE DIAGNOSTIC, TEST UNIT READY, media serial number, and aliases.
- Mode page structures for control, control extension, disconnect/reconnect, informational exceptions, and power condition pages.
- NAA identifier layouts and helper macros including `NAA_IEEE_EXT_*`, `NAA_IEEE_REG_*`, and `NAA_IEEE_REG_EXT_*`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/cdio.h`, `sys/sysmacros.h`, `sys/scsi/generic/commands.h`, and `sys/scsi/impl/commands.h`. It relies on illumos bitfield and multi-byte SCSI access macros such as `DECL_BITFIELD*`, `SCSI_READ*`, and `SCSI_MK*`.

## Research Notes
The file uses `#pragma pack(1)` around protocol structures, so it is intended to match on-the-wire SCSI layouts rather than host-natural C layout. Several structures use one-element flexible arrays.

## Notable Risks
- Any layout, packing, endian, or bitfield change can break SCSI protocol interoperability.
- Flexible array structures must be sized from protocol length fields.
- Several opcode enum names alias the same numeric opcode for different device classes; command interpretation depends on device type and CDB format.
