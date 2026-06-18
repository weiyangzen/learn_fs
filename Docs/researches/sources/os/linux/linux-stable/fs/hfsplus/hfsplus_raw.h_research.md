# File Research: sources/os/linux/linux-stable/fs/hfsplus/hfsplus_raw.h

## Role

Thin raw-format include wrapper for HFS+ on-disk structure definitions.

## Contents

- SPDX GPL-2.0 license header.
- Historical comment identifying the file as the HFS+ raw on-disk format header and noting that the format information came from Apple Technote #1150.
- Include guard `_LINUX_HFSPLUS_RAW_H`.
- Includes:
  - `<linux/types.h>`
  - `<linux/hfs_common.h>`

## Research Notes

This file no longer declares raw HFS+ structures directly. Instead, it delegates to common Linux HFS/HFS+ definitions in `linux/hfs_common.h`. Local HFS+ source files include this header to maintain the traditional internal include name while sharing raw structure definitions from the common header.
