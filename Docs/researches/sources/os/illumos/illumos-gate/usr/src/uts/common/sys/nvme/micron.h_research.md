# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron.h

## Purpose

`nvme/micron.h` is the Micron vendor aggregation header and shared Micron vendor-log definition point for uncommitted NVMe vendor-specific interfaces.

## Main Interfaces

It includes Micron family headers for 7300, 74x0, x500, and 9550 devices, and defines:

- `MICRON_PCI_VID` = `0x1344`

The packed `micron_vul_ext_smart_t` models Micron's common 256-byte extended SMART log used across several generations, with newer fields marked as 7400+ specific. It includes grown bad block count, max erase count, power-on count, write-protect reason, capacity, erase count, use rate, erase fail, UECC, program fail, read/write bytes, translation size, bad-block statistics, and user erase min/avg/max.

`micron_vul_wp_reason_t` defines write-protect reason bits such as DRAM double-bit error, low spare blocks, capacitor failure, NVRAM checksum, DRAM range, and over-temperature.

## Runtime Use

Micron-specific discovery and telemetry code uses device-family IDs to select the proper log ID and then parses the returned extended SMART payload with this common structure where applicable.

## Dependencies

Includes Micron family headers. Uses `CTASSERT()` via included dependencies or build context, and packed layout pragmas.

## Risks and Invariants

The log layout differs by generation. Fields marked 7400+ must be treated as reserved or unsupported on older devices.

The packed structure must remain exactly `0x100` bytes. Misinterpreting the write-protect bitmask could lead to wrong device health diagnosis.
