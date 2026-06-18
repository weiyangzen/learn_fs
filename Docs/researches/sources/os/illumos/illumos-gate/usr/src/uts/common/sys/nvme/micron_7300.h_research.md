# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_7300.h

## Purpose

`nvme/micron_7300.h` defines uncommitted vendor-specific identifiers and SMART log structures for Micron 7300 Pro/Max devices.

## Main Interfaces

Device IDs:

- `MICRON_7300_PRO_DID` = `0x51a2`
- `MICRON_7300_MAX_DID` = `0x51a3`

`micron_7300_vul_t` defines log `0xca` for an older SMART log and log `0xd0` for the preferred `micron_vul_ext_smart_t`.

The packed `micron_vul_smart_ent_t` is a 12-byte entry with type, reserved bytes, and seven data bytes. `micron_vul_smart_t` contains six fixed entries: writes, reads, throttle, life/temp, power, and power-on temperature. A `CTASSERT()` verifies total size `0x48`.

## Runtime Use

Telemetry consumers may read the legacy `0xca` SMART log or prefer the common extended SMART log at `0xd0` when available.

## Dependencies

Includes `sys/debug.h` and `sys/stdint.h`.

## Risks and Invariants

The legacy entry payload interpretation varies by type and is not self-describing beyond fixed position and type. Consumers should validate types and prefer the extended SMART log where possible.
