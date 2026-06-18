# File Research: sources/local-fs/mtd-utils/include/mtd/ubi-media.h

## Purpose
Defines UBI on-flash media format structures and constants.

## Key Elements
Includes UBI version, erase counter limits, CRC init, EC/VID magic values, volume type/flag/compat constants, EC header, VID header, internal layout volume constants, volume limits, and volume table record layout.

## Dependencies
Uses big-endian Linux types from `asm/byteorder.h`.

## Behavior/Risks
This is persistent media ABI. Fields such as CRCs, sequence numbers, erase counters, and volume table records must remain compatible with kernel UBI.
