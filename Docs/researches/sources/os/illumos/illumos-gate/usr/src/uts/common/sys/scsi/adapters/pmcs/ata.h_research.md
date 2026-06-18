# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata.h

## Purpose
Defines ATA IDENTIFY DEVICE data layout used by the PMCS driver for SATA devices behind the SAS controller.

## Main Interfaces
- Includes `ata8-acs.h` for ATA opcodes and `atapi7v3.h` for SATA FIS structures.
- `ata_identify_t` is a 256-word structure matching the ATA IDENTIFY data block, with named fields for serial number, firmware revision, model number, and generic `wordN` placeholders for the remaining specification words.
- `LBA_CAPACITY(ati)` chooses 28-bit capacity from words 60-61 unless word 83 indicates 48-bit addressing, then builds a 64-bit capacity from words 100-103 with little-endian conversion.

## Dependencies And Relationships
Used by PMCS SATA probing/identify logic to derive target capacity and descriptive strings from IDENTIFY data returned through a SATA command.

## Research Notes
This is a wire-format header. Consumers must treat the contents as little-endian ATA words and avoid native-endian direct interpretation.
