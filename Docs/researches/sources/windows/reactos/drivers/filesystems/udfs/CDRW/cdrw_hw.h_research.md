# File Research: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_hw.h

## Purpose

`cdrw_hw.h` is the packed low-level MMC/SCSI/ATAPI protocol definition header used by the UDFS CD/DVD writer support layer. It defines wire-format command descriptor blocks, response records, mode pages, event blocks, media feature descriptors, profile numbers, sense codes, and optical-disc metadata structures.

## Main Contents

- Defines the central packed `CDB` union for many 6, 10, and 12 byte commands:
  - inquiry, request sense, read/write, format unit, erase, mode sense/select, log sense, start/stop, media removal.
  - CD/DVD-specific commands including read TOC, read header, read CD/MSF, write CD, close track/session, blank, reserve track, set CD speed, synchronize cache, read DVD structure, get configuration, set streaming, send OPC, send cue sheet, report/send key.
  - vendor commands for Plextor and NEC CD-DA reads.
- Defines SCSI operation codes and bus/status constants:
  - `SCSIOP_*` command opcodes.
  - `SCSISTAT_*` status values.
  - `SCSI_SENSE_*`, `SCSI_ADSENSE_*`, and `SCSI_SENSEQ_*` sense key/additional sense mappings.
- Defines optical media response records:
  - inquiry and sense data.
  - read capacity.
  - TOC/session/full TOC/PMA/ATIP/CD-TEXT records.
  - disc info, track info, event status blocks, buffer capacity, mechanical status.
- Defines mode pages:
  - read/write recovery, read recovery, write parameters, caching, CD device params, CD audio, power condition, failure reporting, timeout/protect, Philips sector type, capabilities/mechanical status, MRW.
- Defines format and capacity structures:
  - `FORMAT_LIST_HEADER`, `CDRW_FORMAT_DESCRIPTOR`, `DVD_FORMAT_DESCRIPTOR`, `FORMAT_UNIT_PARAMETER_LIST`, format-capacity descriptors.
- Defines GET CONFIGURATION feature/profile structures:
  - profile list and profile descriptors.
  - removable media, multiread, CD read, formattable, MRW, DVD+RW/+R, DVD write, streaming, BD read/write descriptors.
- Defines DVD/CSS key exchange and structure records:
  - copyright, disk key, AGID, challenge key, title key, ASF records.

## Integration Notes

This file is included by `cdrw_usr.h` and likely by the CDRW implementation files to build SCSI CDBs and parse device responses. Its structures are packed with `#pragma pack(push, 1)`, so callers must treat them as on-the-wire byte layouts, not native host records.

## Risks And Edge Cases

- Heavy use of C bitfields in packed wire structures is compiler- and endian-sensitive. The code assumes the Windows/x86 layout used by the original driver.
- Many multi-byte SCSI/MMC fields are stored as byte arrays in big-endian order. Callers must byte-swap explicitly.
- The header carries old and newer MMC definitions together, including obsolete and vendor-specific commands, so consumers need feature/profile checks before issuing commands.
- Several names contain historical typos such as `FormatCapcity`, `REMOVALE`, `OWERWRITE`, and `BlueRay`; these are ABI/source compatibility names and should not be casually renamed.
