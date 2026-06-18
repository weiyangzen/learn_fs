# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.h

## Purpose

Header for DPDK compressdev accel module enablement and PMD selection.

## Key Contents

- `enum compress_pmd`:
  - `COMPRESS_PMD_AUTO`
  - `COMPRESS_PMD_QAT_ONLY`
  - `COMPRESS_PMD_MLX5_PCI_ONLY`
  - `COMPRESS_PMD_UADK_ONLY`
  - `COMPRESS_PMD_MAX`
- Declares:
  - `void accel_dpdk_compressdev_enable(void);`
  - `int accel_compressdev_enable_probe(enum compress_pmd *opts);`

## Relationships

- Used by module implementation and RPC file.
