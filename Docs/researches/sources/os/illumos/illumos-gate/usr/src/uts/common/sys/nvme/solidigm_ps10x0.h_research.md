# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_ps10x0.h

## Purpose

`nvme/solidigm_ps10x0.h` defines uncommitted vendor-specific identifiers and log aliases for Solidigm/Intel PS1010 and PS1030 devices.

## Main Interfaces

Device and subsystem IDs identify PS1010/PS1030 and U.2/E3 variants:

- `SOLIDIGM_PS10X0_DID` = `0x2B59`
- `SOLIDIGM_PS1010_U2_SDID`, `SOLIDIGM_PS1010_E3_SDID`
- `SOLIDIGM_PS1030_U2_SDID`, `SOLIDIGM_PS1030_E3_SDID`

`solidigm_ps10x0_vul_t` maps OCP logs plus Solidigm SMART log `0xca` and temperature log `0xd5`. The SMART log uses `solidigm_vul_smart_log_t`; the temperature log uses `solidigm_vul_temp_t`.

## Runtime Use

Consumers match device/subsystem IDs, request OCP or Solidigm-specific log pages, and parse SMART entries allowing holes.

## Dependencies

Uses OCP constants and common Solidigm structures, normally through inclusion from `solidigm.h`.

## Risks and Invariants

Direct inclusion without prior OCP/common Solidigm definitions may require include-order care. SMART log parsing must not assume all possible entries are present.
