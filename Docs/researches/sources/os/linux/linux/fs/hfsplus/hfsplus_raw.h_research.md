# File Research: sources/os/linux/linux/fs/hfsplus/hfsplus_raw.h

## Role

Thin raw-format include wrapper for HFS+ on-disk structure definitions.

## Contents

- SPDX GPL-2.0 license header.
- Historical comment identifying the file as the HFS+ raw on-disk format header and noting Apple Technote #1150 as the source for format information.
- Include guard `_LINUX_HFSPLUS_RAW_H`.
- Includes:
  - `<linux/types.h>`
  - `<linux/hfs_common.h>`

## Research Notes

This file no longer declares raw HFS+ structures directly. It preserves the traditional internal include name while delegating actual raw format definitions to the common Linux HFS/HFS+ header.
