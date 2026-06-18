# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn861.h

## Purpose

`nvme/wdc_sn861.h` defines uncommitted Sandisk/WDC SN861 vendor-specific IDs, OCP log aliases, and vendor command constants.

## Main Interfaces

Device IDs distinguish form factors:

- `WDC_SN861_DID_E1` = `0x2750`
- `WDC_SN861_DID_U2` = `0x2751`
- `WDC_SN861_DID_E3` = `0x2752`

`wdc_sn861_vul_t` maps OCP SMART, error recovery, firmware activation, latency, device capabilities, and unsupported requirements.

Vendor command constants use opcode `0xd2` for PCIe eye diagram retrieval and hardware revision retrieval. Eye retrieval uses `WDC_SN861_VUC_EYE_CDW12`, lane in `cdw13`, and a fixed upper-bound length `WDC_SN861_VUC_EYE_LEN`. Hardware revision uses `WDC_SN861_VUC_HWREV_CDW12`.

## Runtime Use

Consumers match SN861 variants by device ID, parse standard OCP logs, and use vendor passthrough for eye diagram or hardware revision commands.

## Dependencies

Includes `sys/debug.h`, `sys/stdint.h`, and `sys/nvme/ocp.h`.

## Risks and Invariants

The eye diagram command returns a large fixed upper-bound payload. Callers must validate buffer size, lane selection, and command timeout.

Both vendor commands share opcode `0xd2` and differ by `cdw12`; subcommand selection must be exact.
