# File Research: sources/local-fs/mtd-utils/fectest.c

## Purpose
Standalone forward-error-correction test for multicast image packet recovery.

## Key Elements
Creates deterministic random eraseblock-sized data, splits it into packets, intentionally drops selected packet numbers, uses `fec_new`, `fec_encode`, and `fec_decode`, compares the recovered data, and writes `before`/`after` files on mismatch.

## Dependencies
Depends on `mcast_image.h` for FEC APIs and packet size, and includes `crc32.h` though this file does not call CRC directly.

## Behavior/Risks
Test harness only. Packet drop patterns and random seed are hard-coded; allocated packet buffers are not freed before process exit.
