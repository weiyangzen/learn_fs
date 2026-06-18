# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/phison.h

## Purpose

`nvme/phison.h` defines uncommitted Phison vendor-specific NVMe IDs and OCP log aliases for known Phison devices.

## Main Interfaces

Vendor/device IDs:

- `PHISON_PCI_VID` = `0x1987`
- `PHISON_X200_DID` = `0x5302`

`phison_x200_vul_t` maps X200 log aliases to OCP SMART, error recovery, firmware activation, latency, device capabilities, and unsupported requirements.

## Runtime Use

Device-specific discovery code matches Phison X200 devices and treats the listed vendor logs as OCP Datacenter SSD payloads.

## Dependencies

Includes `sys/nvme/ocp.h`.

## Risks and Invariants

The header declares an uncommitted interface. Correctness depends on the X200 conforming to OCP log layouts for these IDs.
