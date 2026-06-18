# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm.h

## Purpose

`nvme/solidigm.h` aggregates Solidigm and legacy Intel NVMe vendor definitions, and defines common packed payload structures shared across Solidigm device families.

## Main Interfaces

Vendor IDs:

- `INTEL_PCI_VID` = `0x8086`
- `SOLIDIGM_PCI_VID` = `0x25e`

The header includes P5xxx and PS10x0 family headers.

Common packed structures:

- `solidigm_smart_ent_t`: 12-byte device-specific SMART entry with type, normalized value, raw six-byte payload, and reserved bytes.
- `solidigm_smart_type_t`: entry type IDs for program/erase failures, wear level, E2E/CRC errors, timed media wear/read/timer values, in-flight read/write, thermal throttling, retry buffer overflow, PLL loss, NAND/host write, system life, NAND read, firmware download availability, read/write collision, and XOR stats.
- `solidigm_vul_smart_log_t`: up to one 512-byte log page of 12-byte entries.
- `solidigm_vul_temp_t`: 112-byte common temperature log with current, over-threshold, lifetime, composite high/low, warning max, minimum operating, and estimated offset fields.

`CTASSERT()` checks enforce structure sizes and range expectations.

## Runtime Use

Solidigm family-specific headers refer to these common structures for SMART and temperature logs. Consumers should parse SMART entries by entry type because order may vary or holes may exist.

## Dependencies

Includes `solidigm_p5xxx.h` and `solidigm_ps10x0.h`. Uses packed layout and `CTASSERT()`.

## Risks and Invariants

`SOLIDIGM_PCI_VID` is written as `0x25e`; consumers should treat it as the numeric value from the header, though conventional PCI vendor IDs are often displayed zero-padded.

The SMART log can contain entries in arbitrary order. Code that assumes array index equals semantic meaning may misread telemetry.
