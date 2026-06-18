# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_9550.h

## Purpose

`nvme/micron_9550.h` defines uncommitted vendor-specific identifiers and OCP log mappings for Micron 9550 series NVMe devices.

## Main Interfaces

Device IDs:

- `MICRON_9550_PRO_DID` = `0x51bb`
- `MICRON_9550_MAX_DID` = `0x51bd`

`micron_9500_vul_t` maps Micron 9550 log aliases to OCP Datacenter SSD logs: SMART, error recovery, firmware activation, latency, device capability, unsupported requirements, and telemetry.

## Runtime Use

Consumers identify 9550 devices by PCI ID and use OCP log structures from `ocp.h` for the listed telemetry pages.

## Dependencies

Uses OCP log constants, but does not directly include `ocp.h`; it is included indirectly through the aggregation context in `micron.h` only if already available. Direct inclusion may require include-order care.

## Risks and Invariants

The enum type name `micron_9500_vul_t` differs from the file/device family name `9550`, likely a naming inconsistency. Consumers should use the constants, not infer family from the typedef name.
