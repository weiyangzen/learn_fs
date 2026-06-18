# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_x500.h

## Purpose

`nvme/micron_x500.h` defines uncommitted vendor-specific identifiers and OCP log mappings for Micron 6500 and 7500 series devices.

## Main Interfaces

Device IDs:

- `MICRON_6500_ION_DID` = `0x51b9`
- `MICRON_7500_PRO_DID` = `0x51b7`
- `MICRON_7500_MAX_DID` = `0x51b8`

`micron_x500_vul_t` maps OCP SMART, error recovery, firmware activation, latency, device capability, and unsupported-requirements logs.

## Runtime Use

Device matching code uses the PCI device ID to select these log-page aliases, then parses payloads with OCP structures.

## Dependencies

Includes `sys/nvme/ocp.h`.

## Risks and Invariants

The interface is uncommitted and vendor-specific. The x500 family name spans multiple product generations, so future devices may need additional payload distinctions even when log IDs are shared.
