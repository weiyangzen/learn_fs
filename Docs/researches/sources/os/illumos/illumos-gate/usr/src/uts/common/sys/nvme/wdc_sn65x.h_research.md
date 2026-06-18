# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn65x.h

## Purpose

`nvme/wdc_sn65x.h` defines uncommitted vendor-specific IDs, log IDs, temperature sample indexes, and SMART log layout for WDC SN650 and SN655 devices.

## Main Interfaces

Device IDs:

- `WDC_SN650_DID` = `0x2720`
- `WDC_SN655_DID` = `0x2722`

`wdc_sn65x_vul_t` defines OCP SMART, common power log `0xc5`, common temperature log `0xc6`, and unique SMART log `0xca`.

`wdc_sn65x_temp_sample_t` enumerates temperature sample positions including board sensors, inlet/outlet, NAND, front-end, flash modules, thermistor, averages, and `WDC_SN65X_TEMP_NSAMPLES`.

The packed `wdc_vul_sn65x_smart_ent_t` is a 12-byte customer-unique SMART entry. `wdc_vul_sn65x_smart_t` defines fixed entries for program/erase failures, wear, E2E, CRC, timed wear/read/timer, thermal throttling, retry overflow, PLL loss, NAND written, and host written. `wdc_sn65x_smart_ent_id_t` defines expected entry IDs.

## Runtime Use

Consumers request SN65x power/temp/SMART logs and use the family-specific sample and entry enums to interpret variable/common structures and fixed unique SMART entries.

## Dependencies

Includes `sys/debug.h`, `sys/stdint.h`, and `sys/nvme/ocp.h`.

## Risks and Invariants

The SMART enum contains spelling inconsistencies such as `END_ID`, `ETOE`, and `THROTLE`; consumers must use the defined names or compare numeric values.

The unique SMART log comment says entry IDs should be validated. Failing to validate IDs can silently mislabel telemetry if firmware layout changes.
