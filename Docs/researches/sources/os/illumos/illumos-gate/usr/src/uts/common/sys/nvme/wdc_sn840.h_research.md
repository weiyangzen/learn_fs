# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn840.h

## Purpose

`nvme/wdc_sn840.h` defines uncommitted WDC SN840 vendor-specific IDs, log IDs, device manageability entry IDs, temperature sample indexes, and packed log structures.

## Main Interfaces

Device ID:

- `WDC_SN840_DID` = `0x2500`

`wdc_sn840_vul_t` defines log IDs for EOL, device manageability, PCIe SI, power, temperature, firmware activation, and CCDS info.

Packed payloads include:

- `wdc_vul_sn840_eol_t`: 118-byte EOL status log with read/write amplification, PLR, failure counts, vendor/customer/system status, and state fields.
- `wdc_vul_sn840_fw_act_ent_t`: 48-byte firmware activation entry.
- `wdc_vul_sn840_fw_act_hdr_t`: 16-byte firmware activation header with version, entry count, and entry length.
- `wdc_vul_sn840_ccds_info_t`: 36-byte CCDS information block.

`wdc_sn840_vsd_id_t` enumerates many device manageability entry IDs, including firmware versions, capacities, supported logs/features, form factor, namespace details, part/serial/product strings, thermal/assert/EOL status, and reset sequence metadata. `wdc_sn840_vsd_ns_id_t` defines namespace-scoped supported log/feature IDs. `wdc_sn840_temp_sample_t` defines temperature sample indexes.

## Runtime Use

Consumers parse SN840 log pages by log ID. Device manageability logs use common `wdc_vsd_t` and `wdc_cbs_t` structures from `wdc.h`, with each entry ID determining whether the payload is integer or counted byte string.

## Dependencies

Includes `sys/debug.h` and `sys/stdint.h`; `sys/debug.h` is included twice.

## Risks and Invariants

Several logs are variable-length or table-based. Consumers must use header entry counts/lengths and VSD lengths rather than fixed buffer assumptions.

`WDC_SN840_LOG_PCIE_SI` is known to exist but has unknown data format; tools should expose raw data or mark it unsupported rather than inventing a parser.

The temperature enum ends with `WDC_SN840_TEMP_NSMAPLES`, a spelling typo that is part of the header API.
