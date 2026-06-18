# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fflp_hash.h

## Purpose
Declares CRC/hash helper functions used by FFLP flow hashing.

## Main Interfaces
- CRC initialization and computation:
  - `nxge_crc32c_init()`
  - `nxge_crc32c()`
  - `nxge_crc_ccitt_init()`
  - `nxge_crc_ccitt()`
- H1 hash computation variants:
  - `nxge_compute_h1_table1()`
  - `nxge_compute_h1_table4()`
  - `nxge_compute_h1_serial()`
  - `nxge_init_h1_table()`
- Macro aliases:
  - `nxge_compute_h2()` maps to CCITT CRC.
  - `nxge_compute_h1()` maps to the table4 implementation.

## Dependencies And Relationships
This header is consumed by FFLP classification/hash implementation code that computes H1/H2 values for FCRAM lookup entries.

## Research Notes
Despite the filename, the include guard is `_SYS_NXGE_NXGE_CRC_H`, reflecting its CRC-helper role.
