# File Research: sources/os/linux/linux/fs/befs/endian.h

## Purpose
Centralizes BeFS endian conversion for scalar filesystem-endian types and composite structures.

## Main Helpers
- Scalar conversions:
  - `fs64_to_cpu()` / `cpu_to_fs64()`
  - `fs32_to_cpu()` / `cpu_to_fs32()`
  - `fs16_to_cpu()` / `cpu_to_fs16()`
- Composite conversions:
  - `fsrun_to_cpu()`: disk block run to host block run.
  - `cpu_to_fsrun()`: host block run to disk block run.
  - `fsds_to_cpu()`: disk datastream to host datastream, including all direct runs and range fields.

## Behavior
Conversion is driven by `BEFS_SB(sb)->byte_order`, set during superblock loading from the filesystem byte-order marker.

## Research Notes
Because BeFS volumes may be big- or little-endian, all disk field access depends on these helpers. The `fs*` types are `__bitwise`, making sparse-style type checking possible.
