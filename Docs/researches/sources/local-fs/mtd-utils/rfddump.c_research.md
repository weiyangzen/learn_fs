# File Research: sources/local-fs/mtd-utils/rfddump.c

## Purpose
Dumps a Resident Flash Disk (RFD) formatted NOR image into a linear sector file.

## Key Elements
Reads MTD NOR geometry or a user-specified block size, scans block headers for RFD magic, builds a logical-sector-to-physical-offset map from header entries, reports duplicate/out-of-range mappings, and writes reconstructed 512-byte sectors, filling unmapped sectors with zeroes.

## Dependencies
Uses MTD geometry, POSIX I/O, getopt, endian helpers, and fixed RFD constants.

## Behavior/Risks
Targets NOR/RFD layouts only. CHS-style capacity calculation uses 63 sectors per track and can leave unmapped sectors blank. The custom block-size mode treats input as a regular image and trusts user geometry.
