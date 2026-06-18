# File Research: sources/virtualization/qemu/tools/i386/rapl-msr-index.h

## Purpose
Small header defining the RAPL MSR allowlist used by `qemu-vmsr-helper.c`.

## Contents
Defines:
- `MSR_RAPL_POWER_UNIT` as `0x00000606`
- `MSR_PKG_POWER_LIMIT` as `0x00000610`
- `MSR_PKG_ENERGY_STATUS` as `0x00000611`
- `MSR_PKG_POWER_INFO` as `0x00000614`

## Integration
`qemu-vmsr-helper.c` includes this header and accepts only these register IDs in `is_msr_allowed()`.

## Filesystem/Storage Relevance
None directly. It supports the virtualization helper’s controlled access to host MSR device files.
