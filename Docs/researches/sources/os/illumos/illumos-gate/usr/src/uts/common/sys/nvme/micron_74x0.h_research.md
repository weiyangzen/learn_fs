# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_74x0.h

## Purpose

`nvme/micron_74x0.h` defines Micron 7400/7450 Pro/Max device IDs and the vendor log ID for the extended SMART log.

## Main Interfaces

Device IDs:

- `MICRON_7400_PRO_DID` = `0x51c0`
- `MICRON_7400_MAX_DID` = `0x51c1`
- `MICRON_7450_PRO_DID` = `0x51c3`
- `MICRON_7450_MAX_DID` = `0x51c4`

`micron_74x0_vul_t` defines `MICRON_74x0_LOG_EXT_SMART` = `0xe1`.

## Runtime Use

Consumers match device IDs and request log page `0xe1`, interpreted using the common Micron extended SMART structure from `micron.h`.

## Dependencies

Self-contained with C++ guards; normally included through `micron.h`.

## Risks and Invariants

The file relies on the common Micron header for the actual payload structure. Device ID matching must distinguish Pro/Max variants but the log ID is shared.
