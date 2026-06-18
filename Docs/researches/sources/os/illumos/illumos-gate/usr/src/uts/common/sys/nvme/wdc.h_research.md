# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc.h

## Purpose

`nvme/wdc.h` aggregates WDC/Sandisk vendor-specific NVMe definitions and common WDC payload structures and vendor command constants.

## Main Interfaces

Includes WDC family headers for SN840, SN65x, and SN861. Defines:

- `WDC_PCI_VID` = `0x1b96`

Common packed structures:

- `wdc_vul_power_t`: variable-length power sample log, samples in milliwatts.
- `wdc_vul_temp_t`: variable-length temperature sample log, temperatures in Celsius with family-specific sample-index enums.
- `wdc_vsd_t`: variable-length device manageability entry with length, ID, and data; entries are 4-byte aligned.
- `wdc_cbs_t`: counted byte string with little-endian length and non-null-terminated data.
- `wdc_e6_header_t`: 8-byte diagnostic dump header for opcode `0xe6`.

Vendor command constants cover the E6 diagnostic dump command, destructive resize command `0xcc`, and assert clear/inject command `0xd8`.

## Runtime Use

Family-specific headers reuse the common power/temp/manageability structures. Diagnostic dump readers first fetch the E6 header to determine total byte size, then read dword ranges using command offset fields. Resize and assert commands use specific subcommand encodings in command dwords.

## Dependencies

Includes the WDC family headers. Uses packed layout and `CTASSERT()`.

## Risks and Invariants

The resize command is explicitly destructive. Tooling must gate it behind strong user confirmation and correct lock/state checks.

`wdc_cbs_t` is not a C string; code must obey `cbs_len` and account for 4-byte padding.

The E6 dump size is stored as a big-endian-style size field while commands use dword counts, so byte/dword conversion and endian handling are critical.
