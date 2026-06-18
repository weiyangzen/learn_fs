# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia_cd8.h

## Purpose

`nvme/kioxia_cd8.h` defines uncommitted vendor-specific NVMe identifiers and log layouts for Kioxia CD8 and CD8P devices.

## Main Interfaces

Device IDs:

- `KIOXIA_CD8_DID` = `0x1f`
- `KIOXIA_CD8P_DID` = `0x2b`

`kioxia_cd8_vul_t` maps supported vendor log IDs, mostly to OCP Datacenter SSD logs, plus `KIOXIA_CD8_LOG_EXTSMART` at `0xca`.

The packed `kioxia_extsmart_ent_t` is a 12-byte SMART entry with ID, normalized value, raw six-byte value, and reserved bytes. `kioxia_smart_type_t` defines known entry IDs such as program fail, erase fail, wear level, E2E error, CRC error, NAND write, and host write.

`kioxia_vul_cd8_smart_t` maps the 512-byte CD8 extended SMART log layout, including fixed positions for Kioxia-specific entries and later standard SMART-like entries. `CTASSERT()` checks enforce 12-byte entries and 512-byte log size outside smatch.

## Runtime Use

Consumers issue the relevant vendor log-page request and cast/parse the returned 512-byte buffer according to the packed structures. Entry IDs should be validated when interpreting fields.

## Dependencies

Includes `sys/debug.h` and `sys/nvme/ocp.h`.

## Risks and Invariants

All structures must remain packed and size-checked against vendor manuals. Misalignment or wrong reserved-region sizes would misinterpret device telemetry.

The file is guarded for smatch because the current checker cannot handle packed structure size assertions.
