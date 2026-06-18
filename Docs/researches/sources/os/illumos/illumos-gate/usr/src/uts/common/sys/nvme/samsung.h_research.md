# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/samsung.h

## Purpose

`nvme/samsung.h` defines uncommitted Samsung vendor-specific NVMe IDs and OCP log aliases for Samsung PM9D3 devices.

## Main Interfaces

Vendor/device IDs:

- `SAMSUNG_PCI_VID` = `0x144d`
- `SAMSUNG_PM9D3_DID` = `0xa900`

`samsung_pm9d3_vul_t` maps PM9D3 logs to OCP SMART, error recovery, firmware activation, latency, device capabilities, unsupported requirements, TCG, and telemetry logs.

## Runtime Use

Discovery/telemetry code matches Samsung PM9D3 devices and parses the listed vendor logs with OCP structures.

## Dependencies

Includes `sys/nvme/ocp.h`.

## Risks and Invariants

The file comment incorrectly says it contains entries for known Phison devices, a copy/paste documentation error. The constants themselves are Samsung-specific.

OCP telemetry and TCG logs require OCP 2.5-aware parsing; older OCP assumptions are insufficient.
