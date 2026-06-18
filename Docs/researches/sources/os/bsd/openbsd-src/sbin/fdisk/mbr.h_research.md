# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.h

## Purpose
Declares internal MBR representation and operations.

## Key Contents
- `struct mbr` stores:
  - first EMBR LBA
  - current MBR/EMBR LBA
  - boot code
  - four internal partition entries
  - signature
  - leading zero count from original DOS MBR
- Exposes default boot MBR `default_dmbr`.
- Declares print, init, read, recover, write, and validation functions.

## Notes
The internal representation carries extended-partition context alongside ordinary MBR data.
